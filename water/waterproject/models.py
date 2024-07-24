from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Create your models here.
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('mineralwater', 'Mineral Water'),
        ('waterjug', 'Water Jug'),
        ('waterpet', 'Water Pet'),
    ]
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    usersurname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField()
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')  # `Product` yerine `products`
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # `Order` yerine `order`
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # `Product` yerine `product`
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order #{self.order.pk}"


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
