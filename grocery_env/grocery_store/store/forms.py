from django import forms
from .models import Product, Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'address', 'zipcode', 'city', )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address',
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your zipcode',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city',
            }),
        }
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'product_name', 'product_id', 'description', 'price', 'image',)
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
            'product_name': forms.TextInput(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
            'price': forms.TextInput(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
            'product_id': forms.TextInput(attrs={
                'class': 'w-full p-4 border border-gray-200'
            }),
        }