from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.api_home, name='api_home'),
    path('api_home/', api_views.api_home, name='api_home_explicit'),
    path('categories/', api_views.CategoryListAPI.as_view(), name='api_categories'),
    path('products/', api_views.ProductListAPI.as_view(), name='api_products'),
    path('products/featured/', api_views.FeaturedProductsAPI.as_view(), name='api_featured_products'),
    path('products/<int:pk>/', api_views.ProductDetailAPI.as_view(), name='api_product_detail'),
    path('wishlist/', api_views.WishlistAPI.as_view(), name='api_wishlist'),
    path('wishlist/<int:pk>/', api_views.WishlistDetailAPI.as_view(), name='api_wishlist_detail'),
    path('wishlist/move_to_cart/', api_views.WishlistMoveToCartAPI.as_view(), name='api_wishlist_move_to_cart'),
    path('cart/', api_views.CartAPI.as_view(), name='api_cart'),
    path('cart/<int:pk>/', api_views.CartDetailAPI.as_view(), name='api_cart_detail'),
    path('checkout/whatsapp/', api_views.CheckoutWhatsAppAPI.as_view(), name='api_checkout_whatsapp'),
    path('signup/', api_views.SignupAPI.as_view(), name='api_signup'),
]