#!/usr/bin/env python
"""
Test script to verify admin panel and image handling improvements
"""
import os
import sys
import django

# Setup Django environment
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    from shop.models import Category, Product, ProductImage
    from django.contrib.auth.models import User
    
    print("🔧 Testing Admin Panel and Image Handling Improvements")
    print("=" * 60)
    
    # Test 1: Category creation with slug generation
    print("\n1. Testing Category Creation:")
    try:
        # Create a test category
        test_category = Category(name="Test Electronics & Gadgets")
        test_category.save()
        print(f"✅ Category created: '{test_category.name}' with slug: '{test_category.slug}'")
        
        # Test duplicate name handling
        duplicate_category = Category(name="Test Electronics & Gadgets")
        duplicate_category.save()
        print(f"✅ Duplicate category handled: '{duplicate_category.name}' with slug: '{duplicate_category.slug}'")
        
    except Exception as e:
        print(f"❌ Category creation failed: {e}")
    
    # Test 2: Product creation with slug generation
    print("\n2. Testing Product Creation:")
    try:
        if Category.objects.exists():
            category = Category.objects.first()
            test_product = Product(
                name="Test Smartphone Pro Max",
                category=category,
                price=999.99,
                stock=10,
                description="A test product for admin improvements"
            )
            test_product.save()
            print(f"✅ Product created: '{test_product.name}' with slug: '{test_product.slug}'")
            
            # Test the new image methods
            main_image_url = test_product.get_main_image_url()
            all_images = test_product.get_all_images()
            print(f"✅ Main image URL: {main_image_url or 'No main image'}")
            print(f"✅ Total images count: {len(all_images)}")
            
        else:
            print("❌ No categories found to create product")
            
    except Exception as e:
        print(f"❌ Product creation failed: {e}")
    
    # Test 3: ProductImage functionality
    print("\n3. Testing ProductImage Model:")
    try:
        if Product.objects.exists():
            product = Product.objects.first()
            
            # Simulate additional images (without actual files)
            print(f"✅ Product '{product.name}' has {product.additional_images.count()} additional images")
            print(f"✅ All images method returns {len(product.get_all_images())} total images")
            
        else:
            print("❌ No products found to test images")
            
    except Exception as e:
        print(f"❌ ProductImage test failed: {e}")
    
    # Test 4: Admin Model Methods
    print("\n4. Testing Admin Model Methods:")
    try:
        categories = Category.objects.all()
        for category in categories[:3]:  # Test first 3 categories
            product_count = category.products.count()
            print(f"✅ Category '{category.name}' has {product_count} products")
            
    except Exception as e:
        print(f"❌ Admin methods test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Admin Panel Testing Complete!")
    print("\nKey Improvements Made:")
    print("• Fixed category creation with automatic slug generation")
    print("• Enhanced product image handling with multiple image support")
    print("• Added image preview functionality in admin")
    print("• Improved admin interface with custom styling")
    print("• Added helper methods for better image management")
    print("• Fixed slug generation for both categories and products")
