from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    order_number = models.PositiveIntegerField(null=True, blank=True)  # Sipariş numarası alanı

    def save(self, *args, **kwargs):
        if self.pk is None:  # Yeni bir sipariş oluşturuluyorsa
            last_order = Order.objects.filter(user=self.user).order_by('-created_at').first()
            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    product_price = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product_name} - {self.quantity} pcs"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_date}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class PersonalInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True,
                              choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def __str__(self):
        return f"{self.name} {self.surname}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100, verbose_name='City')  # Örnek: Balıkesir
    district = models.CharField(max_length=100, verbose_name='District')  # Örnek: Karesi
    neighborhood = models.CharField(max_length=100, verbose_name='Neighborhood')  # Örnek: 2.Sakarya Mah.
    street = models.CharField(max_length=255, verbose_name='Street')  # Örnek: 4020 Sk.
    building_number = models.CharField(max_length=10, verbose_name='Building Number')  # Örnek: No:55
    floor = models.CharField(max_length=10, verbose_name='Floor')  # Örnek: Kat:2
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code', blank=True, null=True)
    country = models.CharField(max_length=100, default='Turkey', verbose_name='Country')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.country_ = f"{self.building_number}, {self.street}, {self.neighborhood}, {self.district}, {self.city}, {self.country}"
        return self.country_
