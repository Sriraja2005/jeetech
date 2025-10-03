from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.conf import settings
from django import forms
from .models import Category, Product, ProductImage, Wishlist, CartItem, Review, UserProfile

# Custom Admin Site Configuration
class CustomAdminSite(admin.AdminSite):
    site_header = "JEE TECH Admin Panel"
    site_title = "JEE TECH Admin"
    index_title = "Welcome to JEE TECH Administration"
    
    def index(self, request, extra_context=None):
        """Custom admin index with helpful information"""
        extra_context = extra_context or {}
        
        # Add quick stats and helpful info
        from django.contrib.auth.models import User
        
        extra_context.update({
            'total_users': User.objects.count(),
            'admin_users': User.objects.filter(is_staff=True).count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
            'show_admin_help': True,
        })
        
        return super().index(request, extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter category name (e.g., Electronics, Fashion)',
                'class': 'form-control'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'Auto-generated from name (optional)',
                'class': 'form-control'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("Category name is required.")
        return name.strip()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('id', 'name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('name',)
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug'),
            'description': 'Enter the category name. The slug will be automatically generated if left empty.'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make slug field optional for new categories
        if not obj:  # Creating new category
            form.base_fields['slug'].required = False
        return form
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def save_model(self, request, obj, form, change):
        # Ensure slug is generated if not provided
        if not obj.slug:
            from django.utils.text import slugify
            base_slug = slugify(obj.name)
            if not base_slug:  # If name is empty or only special chars
                base_slug = f"category-{obj.pk or 'new'}"
            
            # Ensure unique slug
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            obj.slug = slug
        
        try:
            super().save_model(request, obj, form, change)
            if not change:  # New category
                self.message_user(request, f'Category "{obj.name}" was created successfully with slug "{obj.slug}". You can now add products to this category.')
            else:  # Updated category
                self.message_user(request, f'Category "{obj.name}" was updated successfully.')
        except Exception as e:
            self.message_user(request, f'Error saving category: {str(e)}', level='ERROR')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'image_preview', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'is_featured', 'image_preview', 'additional_images_count', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'is_featured')
    date_hierarchy = 'created_at'
    readonly_fields = ('slug', 'image_preview', 'created_at', 'updated_at')
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_featured')
        }),
        ('Main Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 150px; border-radius: 8px;" />', obj.image.url)
        return "No main image"
    image_preview.short_description = 'Main Image Preview'
    
    def additional_images_count(self, obj):
        count = obj.additional_images.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{} images</span>', count)
        return format_html('<span style="color: #999;">No additional images</span>')
    additional_images_count.short_description = 'Additional Images'
    
    def save_model(self, request, obj, form, change):
        # Ensure slug is generated if not provided
        if not obj.slug:
            from django.utils.text import slugify
            base_slug = slugify(obj.name)
            if not base_slug:
                base_slug = f"product-{obj.pk or 'new'}"
            
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            obj.slug = slug
        super().save_model(request, obj, form, change)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_preview', 'alt_text', 'order', 'created_at')
    list_filter = ('created_at', 'product__category')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('order', 'alt_text')
    readonly_fields = ('image_preview', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 80px; border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with enhanced admin user management"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'admin_actions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    # Add custom fieldsets for better organization
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Set is_staff=True to allow admin panel access. Set is_superuser=True for full admin privileges.'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
            'description': 'Create a new user. Check "Staff status" to allow admin panel access.'
        }),
    )
    
    def admin_actions(self, obj):
        """Show quick admin action buttons"""
        actions = []
        
        if not obj.is_staff:
            actions.append(
                f'<a href="#" onclick="makeUserAdmin({obj.pk})" style="color: #007cba; text-decoration: none; margin-right: 10px;">'
                f'Make Admin</a>'
            )
        
        if obj.is_staff and not obj.is_superuser:
            actions.append(
                f'<a href="#" onclick="makeUserSuperuser({obj.pk})" style="color: #e74c3c; text-decoration: none; margin-right: 10px;">'
                f'Make Superuser</a>'
            )
        
        if obj.is_staff:
            actions.append(
                f'<span style="color: #27ae60; font-weight: bold;">Admin User</span>'
            )
        
        return format_html(' | '.join(actions)) if actions else format_html('<span style="color: #999;">Regular User</span>')
    
    admin_actions.short_description = 'Admin Status'
    admin_actions.allow_tags = True
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text for admin fields
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].help_text = (
                'Designates whether the user can log into the admin site and access admin features like '
                'adding/editing products, managing categories, etc.'
            )
        
        if 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].help_text = (
                'Designates that this user has all permissions without explicitly assigning them. '
                'Superusers can manage other admin users and have full system access.'
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Show helpful messages
        if obj.is_superuser:
            self.message_user(request, f'User "{obj.username}" is now a superuser with full admin access.')
        elif obj.is_staff:
            self.message_user(request, f'User "{obj.username}" is now an admin user and can access the admin panel.')
        elif change and 'is_staff' in form.changed_data and not obj.is_staff:
            self.message_user(request, f'User "{obj.username}" admin access has been removed.')
    
    class Media:
        js = ('admin/js/user_admin_actions.js',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')