from django import forms
from .models import Product, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PersonalInfo, Address


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
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class PersonalInfoForm(forms.ModelForm):
    user_email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = PersonalInfo
        fields = ['name', 'surname', 'phone', 'gender', 'user_email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['user_email'].initial = self.user.email


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['city', 'district', 'neighborhood', 'street', 'building_number', 'floor', 'postal_code', 'country']
