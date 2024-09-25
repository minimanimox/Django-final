from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'product_name', 'product_id', 'description', 'price', 'image',)