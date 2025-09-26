# ShopX - Django E-commerce Platform

A complete Django e-commerce application with Bootstrap UI, user authentication, product management, shopping cart, wishlist, reviews, and WhatsApp checkout integration.

## 🚀 Features

### User Features
- **User Authentication**: Sign up, login, logout with Django's built-in auth system
- **Product Browsing**: Browse products with filters (category, price range, search)
- **Product Details**: View detailed product information with images and reviews
- **Shopping Cart**: Add/update/remove items with CSRF protection
- **Wishlist**: Save products for later purchase
- **Reviews**: Rate and review products (one review per user per product)
- **WhatsApp Checkout**: Direct checkout via WhatsApp with order summary

### Admin Features
- **Django Admin Panel**: Complete product and order management
- **Category Management**: Create and manage product categories
- **Product Management**: Add/edit products with images, stock, pricing
- **User Management**: View and manage registered users
- **Review Moderation**: Monitor and manage product reviews

### Technical Features
- **Django Templates**: Server-side rendering with Bootstrap 5
- **CSRF Protection**: All forms protected against CSRF attacks
- **JWT API**: RESTful API with JWT authentication
- **Django Messages**: User feedback with Bootstrap alerts
- **Media Files**: Product image upload and serving
- **Pagination**: Efficient product listing with pagination
- **Responsive Design**: Mobile-friendly Bootstrap UI

## 📋 Requirements

- Python 3.8+
- Django 5.0.1
- PostgreSQL/MySQL (optional, SQLite by default)

## 🛠️ Installation

### 1. Clone the repository
```bash
cd backend
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and update:
# - SECRET_KEY (generate a new one for production)
# - WHATSAPP_NUMBER (your WhatsApp business number)
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Collect static files (optional for development)
```bash
python manage.py collectstatic --noinput
```

### 8. Run development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## 📁 Project Structure

```
backend/
├── backend/            # Django project settings
│   ├── settings.py     # Main settings file
│   ├── urls.py         # Root URL configuration
│   └── wsgi.py         # WSGI configuration
├── shop/               # Main application
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── forms.py        # Django forms
│   ├── filters.py      # Product filters
│   ├── serializers.py  # API serializers
│   ├── api_views.py    # API endpoints
│   ├── urls.py         # App URL patterns
│   └── admin.py        # Admin configuration
├── templates/          # Django templates
│   └── shop/
│       ├── base.html   # Base template
│       ├── home.html   # Homepage
│       ├── product_list.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── wishlist.html
│       ├── login.html
│       └── signup.html
├── media/              # User uploaded files
├── static/             # Static files (CSS, JS)
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# WhatsApp Configuration
WHATSAPP_NUMBER=919999999999  # Include country code without +
```

## 📱 WhatsApp Checkout

The WhatsApp checkout feature allows customers to complete their orders via WhatsApp:

1. Customer adds products to cart
2. Clicks "Checkout via WhatsApp" button
3. WhatsApp opens with pre-filled order message
4. Customer sends message to complete order

### Testing WhatsApp Checkout

1. Add products to cart
2. Go to cart page
3. Click "Checkout via WhatsApp"
4. Verify the message format:
```
Hello! I would like to order:

• Product Name (Qty: 2) - ₹1000
• Another Product (Qty: 1) - ₹500

Total: ₹1500
Customer: John Doe
```

## 🔌 API Endpoints

All API endpoints support JWT authentication:

- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `GET /api/categories/` - List categories
- `GET /api/products/` - List products (with filters)
- `GET /api/products/<id>/` - Product detail
- `GET /api/wishlist/` - User wishlist (auth required)
- `POST /api/wishlist/` - Add to wishlist (auth required)
- `GET /api/cart/` - User cart (auth required)
- `POST /api/cart/` - Add to cart (auth required)
- `POST /api/signup/` - User registration

### API Authentication Example

```javascript
// Get token
fetch('/api/token/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
})
.then(res => res.json())
.then(data => {
  // Use token for authenticated requests
  fetch('/api/cart/', {
    headers: {'Authorization': `Bearer ${data.access}`}
  })
});
```

## 🎨 Customization

### Adding Sample Data

```python
# Django shell
python manage.py shell

from shop.models import Category, Product

# Create categories
electronics = Category.objects.create(name="Electronics")
clothing = Category.objects.create(name="Clothing")

# Create products
Product.objects.create(
    name="Laptop",
    category=electronics,
    price=50000,
    stock=10,
    description="High-performance laptop",
    is_featured=True
)
```

### Customizing Templates

All templates extend `base.html` and use Bootstrap 5 classes. To customize:

1. Edit `templates/shop/base.html` for global changes
2. Modify individual templates for page-specific changes
3. Add custom CSS in `static/css/` directory

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Generate new `SECRET_KEY`
3. Configure allowed hosts
4. Set up PostgreSQL/MySQL database
5. Configure static/media file serving
6. Set up email backend for password reset

### Deploy to Server

```bash
# Install production dependencies
pip install gunicorn whitenoise

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Support

For support, email support@shopx.com or create an issue in the repository.

## ⚠️ Important Notes

- Always use CSRF tokens in forms
- Keep SECRET_KEY secure in production
- Update WHATSAPP_NUMBER in .env
- Configure proper database for production
- Set up proper media file handling in production
- Enable HTTPS in production
- Regular backup of database and media files
