from django.core.management.base import BaseCommand
from shop.models import Product, Category

class Command(BaseCommand):
    help = 'Generate slugs for products and categories that don\'t have them'

    def handle(self, *args, **options):
        # Fix product slugs
        products_without_slugs = Product.objects.filter(slug__isnull=True)
        products_count = products_without_slugs.count()
        
        if products_count > 0:
            self.stdout.write(f'Found {products_count} products without slugs')
            for product in products_without_slugs:
                product.save()  # This will trigger the slug generation in the save method
            self.stdout.write(self.style.SUCCESS(f'Generated slugs for {products_count} products'))
        else:
            self.stdout.write('All products already have slugs')
        
        # Fix category slugs
        categories_without_slugs = Category.objects.filter(slug__isnull=True)
        categories_count = categories_without_slugs.count()
        
        if categories_count > 0:
            self.stdout.write(f'Found {categories_count} categories without slugs')
            for category in categories_without_slugs:
                category.save()  # This will trigger the slug generation in the save method
            self.stdout.write(self.style.SUCCESS(f'Generated slugs for {categories_count} categories'))
        else:
            self.stdout.write('All categories already have slugs')
        
        self.stdout.write(self.style.SUCCESS('Slug generation completed!'))
