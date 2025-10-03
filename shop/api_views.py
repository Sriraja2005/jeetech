from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import quote
from .models import Category, Product, Wishlist, CartItem
from .serializers import (
    CategorySerializer, ProductSerializer,
    WishlistSerializer, CartItemSerializer,
    UserSerializer,
)

def api_home(request):
    return JsonResponse({
        "message": "API is running",
        "endpoints": [
            "/api/categories/",
            "/api/products/",
            "/api/wishlist/",
            "/api/cart/",
            "/api/wishlist/move_to_cart/",
            "/api/checkout/whatsapp/",
            "/api/signup/",
            "/api/token/",
            "/api/token/refresh/",
        ]
    })

# -------- Products --------
class ProductListAPI(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        params = self.request.query_params
        category = params.get('category')
        price_min = params.get('price_min')
        price_max = params.get('price_max')
        name = params.get('name')
        featured = params.get('featured')

        if category:
            qs = qs.filter(category_id=category)
        if price_min:
            qs = qs.filter(price__gte=price_min)
        if price_max:
            qs = qs.filter(price__lte=price_max)
        if name:
            qs = qs.filter(Q(name__icontains=name) | Q(description__icontains=name))
        if featured and featured.lower() in ['true', '1', 'yes']:
            qs = qs.filter(is_featured=True)
        
        return qs.order_by('-created_at')


class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class FeaturedProductsAPI(generics.ListAPIView):
    """API endpoint specifically for featured products on home page"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        # Return featured products, or if none exist, return latest products
        featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')
        if featured_products.exists():
            return featured_products[:8]  # Limit to 8 featured products
        else:
            # Fallback to latest products if no featured products exist
            return Product.objects.all().order_by('-created_at')[:8]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add debug info
        featured_count = Product.objects.filter(is_featured=True).count()
        total_count = Product.objects.count()
        
        print(f"Featured Products API called:")
        print(f"  - Featured products in DB: {featured_count}")
        print(f"  - Total products in DB: {total_count}")
        print(f"  - Returning {len(serializer.data)} products")
        
        return Response(serializer.data)


# -------- Categories --------
class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# -------- Wishlist --------
class WishlistAPI(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistDetailAPI(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


# -------- Cart --------
class CartAPI(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # upsert: if already in cart, increment quantity
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        item, created = CartItem.objects.get_or_create(user=self.request.user, product=product)
        if not created:
            item.quantity += max(1, quantity)
            item.save()
            serializer.instance = item
        else:
            serializer.save(user=self.request.user)


class CartDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# -------- Wishlist -> Cart (move one) --------
class WishlistMoveToCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"detail": "product_id is required"}, status=400)
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)

        # remove from wishlist if exists
        Wishlist.objects.filter(user=request.user, product=product).delete()
        # upsert into cart
        item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            item.quantity += 1
            item.save()
        serializer = CartItemSerializer(item, context={"request": request})
        return Response(serializer.data)


# -------- WhatsApp Checkout --------
class CheckoutWhatsAppAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        admin_number = getattr(settings, 'WHATSAPP_NUMBER', None)
        if not admin_number:
            return Response({"detail": "WhatsApp number not configured"}, status=500)
        items = CartItem.objects.filter(user=request.user).select_related('product')
        if not items:
            return Response({"detail": "Cart is empty"}, status=400)

        lines = ["Order Request:"]
        total = 0.0
        for it in items:
            line_total = float(it.product.price) * it.quantity
            total += line_total
            amount = int(line_total) if float(line_total).is_integer() else round(line_total, 2)
            lines.append(f"{it.quantity}x {it.product.name} = ₹{amount}")
        total_amount = int(total) if float(total).is_integer() else round(total, 2)
        lines.append(f"Total = ₹{total_amount}")
        message = quote("\n".join(lines))
        wa_url = f"https://wa.me/{admin_number}?text={message}"
        return Response({"wa_url": wa_url})


# -------- User Signup --------
class SignupAPI(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]