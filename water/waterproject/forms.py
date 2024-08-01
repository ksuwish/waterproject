from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

class CustomUserCreationForm(UserCreationForm):
        first_name = forms.CharField(max_length=30, required=False)
        last_name = forms.CharField(max_length=30, required=False)
        email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
        phone_number = forms.CharField(max_length=15, required=False)

        class Meta:
            model = User
            fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})