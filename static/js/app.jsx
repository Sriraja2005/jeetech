const { useEffect, useState, useMemo, useCallback } = React;

// --- Auth helpers ---
const tokenKey = 'jwt_access';
function getToken() { return localStorage.getItem(tokenKey); }
function setToken(t) { localStorage.setItem(tokenKey, t); }
function clearToken() { localStorage.removeItem(tokenKey); }
function authFetch(url, options={}) {
  const headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
  const t = getToken();
  if (t) headers['Authorization'] = `Bearer ${t}`;
  return fetch(url, Object.assign({}, options, { headers }));
}

// --- UI helpers ---
function useFadeInOnMount(deps=[]) {
  useEffect(() => {
    // Add a small delay to prevent rapid re-execution
    const timeoutId = setTimeout(() => {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15 });
      
      document.querySelectorAll('[data-animate]:not(.visible)').forEach(el => observer.observe(el));
      
      return () => {
        observer.disconnect();
        clearTimeout(timeoutId);
      };
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, deps);
}

// --- Components ---
function ProductCard({ product, onAdd, onWish, onDetails }) {
  const img = product.image_url || product.image || ('https://picsum.photos/seed/' + (product.id || Math.random()) + '/400/300');
  return (
    <div className="card glass-blur fade-in" data-animate>
      <img src={img} alt={product.name} />
      <h3>{product.name}</h3>
      <div className="meta">
        <span className="price">₹{Number(product.price || 0).toFixed(2)}</span>
        <span>{product.category_name || (product.category && product.category.name) || 'General'}</span>
      </div>
      <div className="actions">
        <button onClick={() => onAdd(product)}>Add to Cart</button>
        <button onClick={() => onWish(product)}>❤ Wishlist</button>
        <button onClick={() => onDetails(product)}>Details</button>
      </div>
    </div>
  );
}

function Filters({ onChange }) {
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState('');
  const [q, setQ] = useState('');
  const [minP, setMinP] = useState('');
  const [maxP, setMaxP] = useState('');
  const [categoriesLoaded, setCategoriesLoaded] = useState(false);

  useEffect(() => {
    if (!categoriesLoaded) {
      fetch('/api/categories/')
        .then(r=>r.json())
        .then(data => {
          setCategories(data);
          setCategoriesLoaded(true);
        })
        .catch(()=>{
          setCategories([]);
          setCategoriesLoaded(true);
        });
    }
  }, [categoriesLoaded]);

  useEffect(() => {
    // Add debouncing to prevent rapid API calls
    const timeoutId = setTimeout(() => {
      onChange({ category, name: q, price_min: minP, price_max: maxP });
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [category, q, minP, maxP, onChange]);

  return (
    <div className="glass-blur" style={{padding:12, display:'grid', gap:10, gridTemplateColumns:'repeat(auto-fit,minmax(140px,1fr))'}}>
      <input className="glass-input" placeholder="Search" value={q} onChange={e=>setQ(e.target.value)} />
      <select className="glass-input" value={category} onChange={e=>setCategory(e.target.value)}>
        <option value="">All Categories</option>
        {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
      <input className="glass-input" type="number" min="0" placeholder="Min ₹" value={minP} onChange={e=>setMinP(e.target.value)} />
      <input className="glass-input" type="number" min="0" placeholder="Max ₹" value={maxP} onChange={e=>setMaxP(e.target.value)} />
    </div>
  );
}

function ProductGrid({ go }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [params, setParams] = useState({});
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  function reload(p={}) {
    // Prevent multiple simultaneous requests
    if (loading && !isInitialLoad) return;
    
    const usp = new URLSearchParams();
    for (const k in p) if (p[k]) usp.set(k, p[k]);
    const qs = usp.toString();
    
    setLoading(true);
    setError(null);
    
    fetch('/api/products/' + (qs ? `?${qs}` : ''))
      .then(r => r.ok ? r.json() : Promise.reject(r))
      .then(data => { 
        setItems(Array.isArray(data) ? data : data.results || []); 
        setIsInitialLoad(false);
      })
      .catch(() => setError('Failed to load products'))
      .finally(() => setLoading(false));
  }

  useEffect(() => { 
    // Only reload if params actually changed
    const timeoutId = setTimeout(() => {
      reload(params);
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, [params]);
  
  // Only run fade animation when items actually change, not on every render
  useFadeInOnMount([items.length]);

  const addToCart = (p) => {
    authFetch('/api/cart/', { method:'POST', body: JSON.stringify({ product_id: p.id, quantity: 1 }) })
      .then(r => { if (r.status === 401) { go('#/login'); } })
      .catch(()=>{});
    const navCart = document.getElementById('nav-cart');
    if (navCart) { navCart.textContent = 'Cart • +1'; setTimeout(()=>{ navCart.textContent = 'Cart'; }, 1200); }
  };

  const addToWishlist = (p) => {
    authFetch('/api/wishlist/', { method:'POST', body: JSON.stringify({ product_id: p.id }) })
      .then(r => { if (r.status === 401) { go('#/login'); } })
      .catch(()=>{});
  };

  if (loading) return <p className="glass-blur" style={{padding:12}}>Loading products…</p>;
  if (error) return <p className="glass-blur" style={{padding:12}}>{error}</p>;

  // Use useCallback to prevent unnecessary re-renders of Filters component
  const handleParamsChange = useCallback((newParams) => {
    setParams(prevParams => {
      // Only update if params actually changed
      const paramsChanged = JSON.stringify(prevParams) !== JSON.stringify(newParams);
      return paramsChanged ? newParams : prevParams;
    });
  }, []);

  return (
    <>
      <Filters onChange={handleParamsChange} />
      <div className="grid">
        {items.map(item => (
          <ProductCard key={item.id || item.pk} product={item}
            onAdd={addToCart}
            onWish={addToWishlist}
            onDetails={() => go(`#/product/${item.id}`)} />
        ))}
      </div>
    </>
  );
}

function ProductDetail({ id, go }) {
  const [p, setP] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch(`/api/products/${id}/`).then(r=>r.json()).then(setP).finally(()=>setLoading(false));
  }, [id]);
  useFadeInOnMount([p]);
  if (loading) return <p className="glass-blur" style={{padding:12}}>Loading…</p>;
  if (!p) return <p className="glass-blur" style={{padding:12}}>Not found</p>;
  const img = p.image_url || p.image || ('https://picsum.photos/seed/' + id + '/800/600');
  return (
    <div className="glass-blur fade-in" data-animate style={{padding:16}}>
      <button onClick={()=>go('#/')} style={{marginBottom:10}}>&larr; Back</button>
      <div style={{display:'grid', gap:16, gridTemplateColumns:'1fr 1fr'}}>
        <img src={img} alt={p.name} style={{width:'100%', borderRadius:12}} />
        <div>
          <h2>{p.name}</h2>
          <p style={{color:'var(--muted)'}}>{p.description}</p>
          <p><strong>Price:</strong> ₹{Number(p.price).toFixed(2)} &nbsp; <strong>Stock:</strong> {p.stock}</p>
          <div style={{display:'flex', gap:10}}>
            <button onClick={()=>authFetch('/api/wishlist/', {method:'POST', body: JSON.stringify({product_id: p.id})}).then(r=>{if(r.status===401)go('#/login')})}>❤ Add to Wishlist</button>
            <button onClick={()=>authFetch('/api/cart/', {method:'POST', body: JSON.stringify({product_id: p.id, quantity:1})}).then(r=>{if(r.status===401)go('#/login')})}>🛒 Add to Cart</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function WishlistPage({ go }) {
  const [items, setItems] = useState([]);
  const load = () => authFetch('/api/wishlist/').then(r=>{ if(r.status===401){go('#/login');return [];} return r.json();}).then(setItems);
  useEffect(load, []);
  useFadeInOnMount([items]);

  const remove = (id) => authFetch(`/api/wishlist/${id}/`, { method:'DELETE' }).then(load);
  const moveToCart = (product_id) => authFetch('/api/wishlist/move_to_cart/', { method:'POST', body: JSON.stringify({ product_id }) }).then(load);

  return (
    <div className="grid">
      {items.map(w => (
        <div key={w.id} className="card glass-blur fade-in" data-animate>
          <ProductCard product={w.product} onAdd={()=>moveToCart(w.product.id)} onWish={()=>remove(w.id)} onDetails={()=>go(`#/product/${w.product.id}`)} />
        </div>
      ))}
      {!items.length && <p className="glass-blur" style={{padding:12}}>No items in wishlist.</p>}
    </div>
  );
}

function CartPage({ go }) {
  const [items, setItems] = useState([]);
  const load = () => authFetch('/api/cart/').then(r=>{ if(r.status===401){go('#/login');return [];} return r.json();}).then(setItems);
  useEffect(load, []);

  const updateQty = (id, quantity) => authFetch(`/api/cart/${id}/`, { method:'PATCH', body: JSON.stringify({ quantity }) }).then(load);
  const remove = (id) => authFetch(`/api/cart/${id}/`, { method:'DELETE' }).then(load);
  const checkout = () => authFetch('/api/checkout/whatsapp/').then(r=>r.json()).then(data => { if (data.wa_url) window.open(data.wa_url, '_blank'); });

  const total = useMemo(() => items.reduce((s, it) => s + (Number(it.line_total)||0), 0), [items]);
  useFadeInOnMount([items]);

  return (
    <div className="glass-blur" style={{padding:12}}>
      <h2>Your Cart</h2>
      {!items.length && <p>No items in cart.</p>}
      {items.map(it => (
        <div key={it.id} className="fade-in" data-animate style={{display:'grid', gridTemplateColumns:'1fr auto auto auto', gap:10, alignItems:'center', padding:'8px 0', borderBottom:'1px solid var(--stroke)'}}>
          <span>{it.product.name}</span>
          <span>₹{Number(it.product.price).toFixed(2)}</span>
          <input type="number" min="1" value={it.quantity} onChange={e=>updateQty(it.id, parseInt(e.target.value||'1'))} className="glass-input" style={{width:70}} />
          <button onClick={()=>remove(it.id)}>Remove</button>
        </div>
      ))}
      <div style={{display:'flex', justifyContent:'space-between', marginTop:12}}>
        <strong>Total: ₹{Number(total).toFixed(2)}</strong>
        <button onClick={checkout} className="btn-primary">Checkout via WhatsApp</button>
      </div>
    </div>
  );
}

function LoginPage({ go }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const submit = (e) => {
    e.preventDefault(); setError('');
    fetch('/api/token/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ username, password }) })
      .then(r => r.ok ? r.json() : r.json().then(d=>Promise.reject(d)))
      .then(data => { setToken(data.access); go('#/'); })
      .catch(()=> setError('Invalid credentials'));
  };
  return (
    <form onSubmit={submit} className="glass-blur" style={{padding:16, display:'grid', gap:10, maxWidth:420}}>
      <h2>Login</h2>
      {error && <p style={{color:'#ff8080'}}>{error}</p>}
      <input className="glass-input" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
      <input className="glass-input" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button type="submit">Login</button>
      <p style={{color:'var(--muted)'}}>No account? <a href="#/signup">Sign up</a></p>
    </form>
  );
}

function SignupPage({ go }) {
  const [form, setForm] = useState({ username:'', password:'', email:'', full_name:'', phone:'', address:'' });
  const [msg, setMsg] = useState('');
  const change = (k,v) => setForm(f => Object.assign({}, f, { [k]: v }));
  const submit = (e) => {
    e.preventDefault(); setMsg('');
    fetch('/api/signup/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(form) })
      .then(r => r.ok ? r.json() : r.json().then(d=>Promise.reject(d)))
      .then(() => { setMsg('Signup successful. Please login.'); setTimeout(()=>go('#/login'), 800); })
      .catch(()=> setMsg('Signup failed. Check details.'));
  };
  return (
    <form onSubmit={submit} className="glass-blur" style={{padding:16, display:'grid', gap:10, maxWidth:520}}>
      <h2>Sign Up</h2>
      {msg && <p>{msg}</p>}
      <input className="glass-input" placeholder="Full Name" value={form.full_name} onChange={e=>change('full_name', e.target.value)} />
      <input className="glass-input" placeholder="Phone" value={form.phone} onChange={e=>change('phone', e.target.value)} />
      <input className="glass-input" placeholder="Email" value={form.email} onChange={e=>change('email', e.target.value)} />
      <input className="glass-input" placeholder="Address" value={form.address} onChange={e=>change('address', e.target.value)} />
      <input className="glass-input" placeholder="Username" value={form.username} onChange={e=>change('username', e.target.value)} />
      <input className="glass-input" type="password" placeholder="Password" value={form.password} onChange={e=>change('password', e.target.value)} />
      <button type="submit">Create Account</button>
      <p style={{color:'var(--muted)'}}>Have an account? <a href="#/login">Login</a></p>
    </form>
  );
}

function Router() {
  const [route, setRoute] = useState(window.location.hash || '#/');
  const go = (h) => { window.location.hash = h; setRoute(h); };
  useEffect(() => {
    const onHash = () => setRoute(window.location.hash || '#/');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  if (route.startsWith('#/product/')) {
    const id = route.split('/')[2];
    return <ProductDetail id={id} go={go} />;
  }
  if (route.startsWith('#/wishlist')) return <WishlistPage go={go} />;
  if (route.startsWith('#/cart')) return <CartPage go={go} />;
  if (route.startsWith('#/login')) return <LoginPage go={go} />;
  if (route.startsWith('#/signup')) return <SignupPage go={go} />;
  return <ProductGrid go={go} />;
}

function App() { return <Router />; }

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
