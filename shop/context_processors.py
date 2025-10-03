from .models import Category, CartItem, Wishlist

def categories(request):
    """Make categories available in all templates"""
    return {
        'categories': Category.objects.all()[:10]
    }

def cart_wishlist_counts(request):
    """Add cart and wishlist counts to all templates"""
    context = {
        'cart_count': 0,
        'wishlist_count': 0,
    }
    
    if request.user.is_authenticated:
        context['cart_count'] = CartItem.objects.filter(user=request.user).count()
        context['wishlist_count'] = Wishlist.objects.filter(user=request.user).count()
    
    return context
