from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


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
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    order_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.pk is None:
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personalinfo')
    name = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(
        max_length=11,  #
        blank=True,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^05\d{9}$',
                code='invalid_phone'
            )
        ]
    )
    gender = models.CharField(max_length=10, blank=True, null=True,
                              choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def __str__(self):
        return f"{self.name} {self.surname}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100, verbose_name='City')
    district = models.CharField(max_length=100, verbose_name='District')
    neighborhood = models.CharField(max_length=100, verbose_name='Neighborhood')
    street = models.CharField(max_length=255, verbose_name='Street')
    building_number = models.CharField(max_length=10, verbose_name='Building Number')
    floor = models.CharField(max_length=10, verbose_name='Floor')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code', blank=True, null=True)
    country = models.CharField(max_length=100, default='Türkiye', verbose_name='Country')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"{self.building_number}, {self.street}, {self.neighborhood}, {self.district}, {self.city},"
                f" {self.country}")

    def save(self, *args, **kwargs):
        full_address = (f"{self.building_number}, {self.street}, {self.neighborhood}, {self.district},"
                        f"{self.city}, {self.country}")

        coordinates = self.get_coordinates(full_address)

        if coordinates:
            self.latitude, self.longitude = coordinates
        else:
            print("Could not retrieve coordinates")

        super().save(*args, **kwargs)

    @staticmethod
    def get_coordinates(address):
        geolocator = Nominatim(user_agent='ademsevinc82@gmail.com')
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                print("Location not found")
                return None
        except GeocoderTimedOut:
            print("Geocoding service timed out. Please try again later.")
            return None
