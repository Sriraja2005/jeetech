#!/usr/bin/env python
"""
Test script to verify category creation works properly
"""
import os
import sys
import django

# Setup Django environment
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    from shop.models import Category
    
    print("🧪 Testing Category Creation")
    print("=" * 50)
    
    # Test 1: Create a simple category
    print("\n1. Testing basic category creation:")
    try:
        test_category = Category(name="Test Electronics")
        test_category.save()
        print(f"✅ Category created successfully: '{test_category.name}' with slug: '{test_category.slug}'")
        
        # Verify it was saved
        saved_category = Category.objects.get(id=test_category.id)
        print(f"✅ Category retrieved from database: '{saved_category.name}'")
        
    except Exception as e:
        print(f"❌ Category creation failed: {e}")
    
    # Test 2: Create category with special characters
    print("\n2. Testing category with special characters:")
    try:
        special_category = Category(name="Home & Garden - Premium!")
        special_category.save()
        print(f"✅ Special category created: '{special_category.name}' with slug: '{special_category.slug}'")
        
    except Exception as e:
        print(f"❌ Special category creation failed: {e}")
    
    # Test 3: Create duplicate name (should get unique slug)
    print("\n3. Testing duplicate category name:")
    try:
        duplicate_category = Category(name="Test Electronics")
        duplicate_category.save()
        print(f"✅ Duplicate category created: '{duplicate_category.name}' with slug: '{duplicate_category.slug}'")
        
    except Exception as e:
        print(f"❌ Duplicate category creation failed: {e}")
    
    # Test 4: List all categories
    print("\n4. All categories in database:")
    try:
        categories = Category.objects.all()
        for cat in categories:
            print(f"   - {cat.name} (slug: {cat.slug})")
        print(f"✅ Total categories: {categories.count()}")
        
    except Exception as e:
        print(f"❌ Failed to list categories: {e}")
    
    # Test 5: Test admin form simulation
    print("\n5. Testing admin form simulation:")
    try:
        from django.contrib.admin.sites import site
        from shop.admin import CategoryAdmin
        from django.http import HttpRequest
        from django.contrib.auth.models import User
        
        # Create a mock request
        request = HttpRequest()
        request.user = User.objects.filter(is_superuser=True).first()
        
        if request.user:
            admin_instance = CategoryAdmin(Category, site)
            
            # Test creating through admin
            new_category = Category(name="Admin Test Category")
            admin_instance.save_model(request, new_category, None, False)
            
            print(f"✅ Admin creation test passed: '{new_category.name}' with slug: '{new_category.slug}'")
        else:
            print("⚠️  No superuser found, skipping admin test")
            
    except Exception as e:
        print(f"❌ Admin form test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Category Creation Test Complete!")
    
    # Cleanup test data
    print("\n🧹 Cleaning up test data...")
    try:
        Category.objects.filter(name__startswith="Test").delete()
        Category.objects.filter(name__startswith="Admin Test").delete()
        Category.objects.filter(name="Home & Garden - Premium!").delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
