from django.core.management.base import BaseCommand
from shop.models import Product, Category
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Create some sample featured products for testing'

    def handle(self, *args, **options):
        # First, ensure we have at least one category
        if not Category.objects.exists():
            self.stdout.write('Creating sample categories...')
            categories_data = [
                'Electronics',
                'Fashion & Clothing',
                'Home & Garden',
                'Sports & Fitness',
                'Books & Media',
                'Health & Beauty'
            ]
            
            for cat_name in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'slug': slugify(cat_name)}
                )
                if created:
                    self.stdout.write(f'Created category: {cat_name}')

        # Get or create some sample products
        categories = list(Category.objects.all())
        
        sample_products = [
            {
                'name': 'Premium Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation and premium sound quality.',
                'price': 299.99,
                'stock': 50,
                'is_featured': True
            },
            {
                'name': 'Smart Fitness Watch',
                'description': 'Advanced fitness tracking with heart rate monitor, GPS, and smartphone integration.',
                'price': 199.99,
                'stock': 30,
                'is_featured': True
            },
            {
                'name': 'Ultra-Slim Laptop',
                'description': 'Powerful and portable laptop perfect for work and entertainment.',
                'price': 899.99,
                'stock': 15,
                'is_featured': True
            },
            {
                'name': 'Professional Camera',
                'description': 'High-resolution digital camera with advanced features for photography enthusiasts.',
                'price': 1299.99,
                'stock': 8,
                'is_featured': True
            },
            {
                'name': 'Gaming Mechanical Keyboard',
                'description': 'RGB backlit mechanical keyboard designed for gaming and productivity.',
                'price': 149.99,
                'stock': 25,
                'is_featured': True
            },
            {
                'name': 'Wireless Charging Pad',
                'description': 'Fast wireless charging pad compatible with all Qi-enabled devices.',
                'price': 49.99,
                'stock': 100,
                'is_featured': True
            },
            {
                'name': 'Bluetooth Speaker',
                'description': 'Portable Bluetooth speaker with excellent sound quality and long battery life.',
                'price': 79.99,
                'stock': 40,
                'is_featured': True
            },
            {
                'name': 'Smart Home Hub',
                'description': 'Central hub for controlling all your smart home devices with voice commands.',
                'price': 129.99,
                'stock': 20,
                'is_featured': True
            }
        ]

        created_count = 0
        updated_count = 0

        for product_data in sample_products:
            # Check if product already exists
            existing_product = Product.objects.filter(name=product_data['name']).first()
            
            if existing_product:
                # Update existing product to be featured
                existing_product.is_featured = True
                existing_product.save()
                updated_count += 1
                self.stdout.write(f'Updated existing product to featured: {existing_product.name}')
            else:
                # Create new product
                category = random.choice(categories)
                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock'],
                    category=category,
                    is_featured=product_data['is_featured']
                )
                created_count += 1
                self.stdout.write(f'Created featured product: {product.name}')

        # Also mark some existing products as featured if they exist
        existing_products = Product.objects.filter(is_featured=False)[:3]
        for product in existing_products:
            product.is_featured = True
            product.save()
            updated_count += 1
            self.stdout.write(f'Marked existing product as featured: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Featured products setup complete!\n'
                f'Created: {created_count} new products\n'
                f'Updated: {updated_count} existing products\n'
                f'Total featured products: {Product.objects.filter(is_featured=True).count()}'
            )
        )
