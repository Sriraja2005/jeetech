import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Search')
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label='All Categories',
        widget=django_filters.widgets.forms.Select(attrs={'class': 'form-select'})
    )
    price_min = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte', 
        label='Min Price',
        widget=django_filters.widgets.forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'})
    )
    price_max = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte', 
        label='Max Price',
        widget=django_filters.widgets.forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'})
    )
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'price_min', 'price_max']
