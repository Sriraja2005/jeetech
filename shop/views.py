from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from urllib.parse import quote
from django.contrib.auth.models import User
from .models import Product, Category, Wishlist, CartItem, Review, UserProfile
from .forms import SignUpForm, ReviewForm, AddToCartForm, UpdateCartForm, UserProfileForm, ProductForm, CategoryForm, ProductImageFormSet
from .filters import ProductFilter

from django.contrib.auth.views import LoginView
from django.contrib import messages

class CustomLoginView(LoginView):
    """Custom LoginView with success messages"""
    template_name = 'shop/login.html'
    
    def form_valid(self, form):
        """Add success message when login is successful"""
        response = super().form_valid(form)
        user = self.request.user
        display_name = user.get_full_name() or user.username
        messages.success(self.request, f'Welcome back, {display_name}! You have been successfully logged in.')
        return response
    
    def form_invalid(self, form):
        """Add error message when login fails"""
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

def home(request):
    featured_products = Product.objects.filter(is_featured=True, stock__gt=0)[:8]
    categories = Category.objects.annotate(product_count=Count('products'))[:6]
    latest_products = Product.objects.filter(stock__gt=0)[:8]
    
    # Add wishlist information for authenticated users
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'index.html', context)

def product_list(request):
    products = Product.objects.filter(stock__gt=0)
    product_filter = ProductFilter(request.GET, queryset=products)
    products = product_filter.qs
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add wishlist information for authenticated users
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'filter': product_filter,
        'page_obj': page_obj,
        'products': page_obj,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    # Try to get by slug first, then by ID if slug fails
    try:
        product = get_object_or_404(Product, slug=slug)
    except:
        # If slug lookup fails, try ID
        try:
            product = get_object_or_404(Product, id=int(slug))
        except (ValueError, Product.DoesNotExist):
            product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    # Handle review form submission
    if request.method == 'POST' and request.user.is_authenticated:
        if not user_review:  # Only allow one review per user per product
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been added successfully!')
                return redirect('product_detail', slug=slug)
        else:
            messages.warning(request, 'You have already reviewed this product.')
    else:
        form = ReviewForm()
    
    # Add to cart form
    cart_form = AddToCartForm()
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': form,
        'cart_form': cart_form,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def add_to_cart(request, slug):
    if request.method == 'POST':
        # Try to get by slug first, then by ID if slug fails
        try:
            product = get_object_or_404(Product, slug=slug)
        except:
            try:
                product = get_object_or_404(Product, id=int(slug))
            except (ValueError, Product.DoesNotExist):
                product = get_object_or_404(Product, slug=slug)
        form = AddToCartForm(request.POST)
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if product.stock < quantity:
                messages.error(request, f'Sorry, only {product.stock} items available in stock.')
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'insufficient_stock', 'available': product.stock})
                return redirect('product_detail', slug=slug)
            
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f'Updated {product.name} quantity in your cart.')
            else:
                messages.success(request, f'Added {product.name} to your cart.')
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart_count = CartItem.objects.filter(user=request.user).count()
                return JsonResponse({'success': True, 'cart_count': cart_count})
            return redirect('cart')
    
    return redirect('product_list')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)

@login_required
@require_POST
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if cart_item.product.stock >= quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            messages.error(request, f'Sorry, only {cart_item.product.stock} items available.')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from your cart.')
    return redirect('cart')

@login_required
def checkout_whatsapp(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    
    # Build WhatsApp message
    message = f"Hello! I would like to order from JEETECH:\n\n"
    total = 0
    
    for item in cart_items:
        item_total = item.get_total_price()
        total += item_total
        message += f"• {item.product.name} (Qty: {item.quantity}) - Rs.{item_total}\n"
    
    message += f"\nTotal: Rs.{total}\n"
    message += f"Customer: {request.user.get_full_name() or request.user.username}\n"
    message += f"Thank you!"
    
    # URL encode the message
    encoded_message = quote(message)
    
    # Get WhatsApp number from settings or use default
    whatsapp_number = getattr(settings, 'WHATSAPP_NUMBER', '919344998602')
    
    # Generate WhatsApp URL
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    # Optional: Clear cart after checkout
    # cart_items.delete()
    
    return redirect(whatsapp_url)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'shop/wishlist.html', context)

@login_required
def toggle_wishlist(request, slug):
    # Try to get by slug first, then by ID if slug fails
    try:
        product = get_object_or_404(Product, slug=slug)
    except:
        try:
            product = get_object_or_404(Product, id=int(slug))
        except (ValueError, Product.DoesNotExist):
            product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        wishlist_item.delete()
        in_wishlist = False
        messages.success(request, f'Removed {product.name} from your wishlist.')
    else:
        in_wishlist = True
        messages.success(request, f'Added {product.name} to your wishlist.')

    # If AJAX request, return JSON (avoid page refresh)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'wishlist_count': wishlist_count,
            'product_id': product.id,
        })

    # Otherwise, return to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'Removed {product_name} from your wishlist.')
    return redirect('wishlist')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'shop/signup.html', {'form': form})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, stock__gt=0)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Wishlist info
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'shop/category_products.html', context)

@login_required
def profile_view(request):
    """User profile page"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Get user's recent orders, wishlist, and cart stats
    cart_items = CartItem.objects.filter(user=request.user)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
        'cart_items_count': cart_items.count(),
        'wishlist_items_count': wishlist_items.count(),
        'cart_total': sum(item.get_total_price() for item in cart_items),
    }
    return render(request, 'shop/profile.html', context)

def about_view(request):
    """About page"""
    return render(request, 'shop/about.html')

def fix_product_slugs(request):
    """Utility view to fix product slugs - for admin use only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    from django.utils.text import slugify
    
    products_fixed = 0
    for product in Product.objects.all():
        if not product.slug or product.slug == 'None':
            product.save()  # This will trigger the improved save method
            products_fixed += 1
    
    messages.success(request, f'Fixed slugs for {products_fixed} products.')
    return redirect('product_list')

def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

# Admin Dashboard Views
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    # Get statistics
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_orders = CartItem.objects.values('user').distinct().count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    
    # Recent products
    recent_products = Product.objects.order_by('-created_at')[:5]
    
    # Top categories by product count
    top_categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:5]
    
    # Recent customers
    recent_customers = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    
    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'low_stock_products': low_stock_products,
        'recent_products': recent_products,
        'top_categories': top_categories,
        'recent_customers': recent_customers,
    }
    return render(request, 'shop/admin_dashboard.html', context)

@staff_member_required
def admin_products(request):
    """Admin products management"""
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'shop/admin_products.html', context)

@staff_member_required
def admin_product_add(request):
    """Add new product"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        is_featured = request.POST.get('is_featured') == 'on'
        image = request.FILES.get('image')
        
        try:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category,
                is_featured=is_featured,
                image=image
            )
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'shop/admin_product_form.html', context)

@staff_member_required
def admin_product_edit(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        product.is_featured = request.POST.get('is_featured') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        try:
            product.category = Category.objects.get(id=category_id)
            product.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'is_edit': True
    }
    return render(request, 'shop/admin_product_form.html', context)

@staff_member_required
def admin_product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('admin_products')
    
    context = {'product': product}
    return render(request, 'shop/admin_product_delete.html', context)

@staff_member_required
def admin_product_add(request):
    """Add new product with multiple images and category creation"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save()
            
            # Handle multiple images
            if formset.is_valid():
                formset.instance = product
                formset.save()
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('admin_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Add New Product'
    }
    return render(request, 'shop/admin_product_form.html', context)

@staff_member_required
def admin_product_edit(request, product_id):
    """Edit existing product with multiple images"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save()
            
            # Handle multiple images
            if formset.is_valid():
                formset.save()
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    
    context = {
        'form': form,
        'formset': formset,
        'product': product,
        'title': f'Edit Product: {product.name}'
    }
    return render(request, 'shop/admin_product_form.html', context)

@staff_member_required
def admin_category_add(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('admin_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category'
    }
    return render(request, 'shop/admin_category_form.html', context)
