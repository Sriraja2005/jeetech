from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, CartItem, UserProfile, Product, Category, ProductImage

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px'})
    )

class UpdateCartForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px', 'min': '1'})
        }

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = UserProfile
        fields = ['address', 'phone']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your full address including street, city, state, postal code'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name (e.g., Electronics, Fashion)',
                'required': True
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("Category name is required.")
        return name.strip()

class ProductForm(forms.ModelForm):
    # Add option to create new category
    new_category = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or enter new category name',
            'id': 'new_category_input'
        }),
        help_text="Leave empty to use existing category, or enter new category name"
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'new_category', 'description', 'price', 'stock', 'image', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'category_select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select existing category"
        self.fields['category'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        
        if not category and not new_category:
            raise forms.ValidationError("Please select an existing category or enter a new category name.")
        
        if category and new_category:
            raise forms.ValidationError("Please choose either an existing category OR enter a new category name, not both.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle new category creation
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            from django.utils.text import slugify
            category, created = Category.objects.get_or_create(
                name=new_category_name.strip(),
                defaults={'slug': slugify(new_category_name.strip())}
            )
            instance.category = category
        
        if commit:
            instance.save()
        return instance

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image description (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            })
        }

# Formset for multiple images
ProductImageFormSet = forms.inlineformset_factory(
    Product, 
    ProductImage, 
    form=ProductImageForm,
    extra=3,  # Show 3 empty forms by default
    can_delete=True,
    fields=['image', 'alt_text', 'order']
)
