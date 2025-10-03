#!/usr/bin/env python
"""
Quick script to create sample products for testing
"""
import os
import sys
import django

# Setup Django environment
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    from shop.models import Category, Product
    from django.utils.text import slugify
    
    print("🚀 Creating Sample Products for Featured Section")
    print("=" * 60)
    
    # Create categories first
    categories_data = [
        'Electronics',
        'Fashion',
        'Home & Garden',
        'Sports',
        'Books'
    ]
    
    categories = {}
    for cat_name in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slugify(cat_name)}
        )
        categories[cat_name] = category
        if created:
            print(f"✅ Created category: {cat_name}")
        else:
            print(f"📋 Category exists: {cat_name}")
    
    # Create sample products
    sample_products = [
        {
            'name': 'Premium Wireless Headphones',
            'category': 'Electronics',
            'description': 'High-quality wireless headphones with noise cancellation and premium sound quality. Perfect for music lovers and professionals.',
            'price': 299.99,
            'stock': 50,
            'is_featured': True
        },
        {
            'name': 'Smart Fitness Watch',
            'category': 'Electronics',
            'description': 'Advanced fitness tracking with heart rate monitor, GPS, and smartphone integration. Track your health 24/7.',
            'price': 199.99,
            'stock': 30,
            'is_featured': True
        },
        {
            'name': 'Ultra-Slim Laptop',
            'category': 'Electronics',
            'description': 'Powerful and portable laptop perfect for work and entertainment. Lightning-fast performance in a sleek design.',
            'price': 899.99,
            'stock': 15,
            'is_featured': True
        },
        {
            'name': 'Designer Jacket',
            'category': 'Fashion',
            'description': 'Stylish and comfortable designer jacket made from premium materials. Perfect for any season.',
            'price': 149.99,
            'stock': 25,
            'is_featured': True
        },
        {
            'name': 'Gaming Mechanical Keyboard',
            'category': 'Electronics',
            'description': 'RGB backlit mechanical keyboard designed for gaming and productivity. Responsive keys with customizable lighting.',
            'price': 149.99,
            'stock': 40,
            'is_featured': True
        },
        {
            'name': 'Smart Home Hub',
            'category': 'Electronics',
            'description': 'Central hub for controlling all your smart home devices with voice commands and mobile app integration.',
            'price': 129.99,
            'stock': 20,
            'is_featured': True
        },
        {
            'name': 'Portable Bluetooth Speaker',
            'category': 'Electronics',
            'description': 'High-quality portable speaker with excellent sound and long battery life. Perfect for outdoor adventures.',
            'price': 79.99,
            'stock': 60,
            'is_featured': True
        },
        {
            'name': 'Professional Camera',
            'category': 'Electronics',
            'description': 'High-resolution digital camera with advanced features for photography enthusiasts and professionals.',
            'price': 1299.99,
            'stock': 8,
            'is_featured': True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for product_data in sample_products:
        category = categories[product_data['category']]
        
        # Check if product already exists
        existing_product = Product.objects.filter(name=product_data['name']).first()
        
        if existing_product:
            # Update existing product to be featured
            existing_product.is_featured = True
            existing_product.price = product_data['price']
            existing_product.stock = product_data['stock']
            existing_product.description = product_data['description']
            existing_product.save()
            updated_count += 1
            print(f"🔄 Updated: {existing_product.name}")
        else:
            # Create new product
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                stock=product_data['stock'],
                category=category,
                is_featured=product_data['is_featured']
            )
            created_count += 1
            print(f"✅ Created: {product.name}")
    
    # Summary
    total_featured = Product.objects.filter(is_featured=True).count()
    total_products = Product.objects.count()
    
    print("\n" + "=" * 60)
    print("🎉 Sample Products Creation Complete!")
    print(f"📊 Statistics:")
    print(f"   • Created: {created_count} new products")
    print(f"   • Updated: {updated_count} existing products")
    print(f"   • Total Featured Products: {total_featured}")
    print(f"   • Total Products: {total_products}")
    print(f"   • Categories: {Category.objects.count()}")
    
    print(f"\n🔗 API Endpoints to test:")
    print(f"   • Featured Products: /api/products/featured/")
    print(f"   • All Products: /api/products/")
    print(f"   • Categories: /api/categories/")
    
    print(f"\n🌐 Visit the home page to see featured products!")
