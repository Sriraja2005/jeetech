from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Redirect services to home (or create a services page if needed)
    path('services/', RedirectView.as_view(url='/', permanent=False), name='services'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    
    # Cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/whatsapp/', views.checkout_whatsapp, name='checkout_whatsapp'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle-wishlist/<slug:slug>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('remove-from-wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about_view, name='about'),
    path('admin/fix-slugs/', views.fix_product_slugs, name='fix_product_slugs'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/products/', views.admin_products, name='admin_products'),
    path('admin-dashboard/product/add/', views.admin_product_add, name='admin_product_add'),
    path('admin-dashboard/product/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-dashboard/product/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
]
