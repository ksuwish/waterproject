# admin.py
from django.contrib import admin
from .models import Category, Product, UserProfile, Order, OrderItem, Payment, Contact

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'usersurname', 'phone_number', 'email')
    search_fields = ('user__username', 'email')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'created_at')
    search_fields = ('user__username',)

class OrderItemAdmin(admin.ModelAdmin):
    
    list_display = ('order', 'product_name', 'product_price', 'quantity')
    search_fields = ('order__user__username', 'product_name')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_date', 'description')
    search_fields = ('user__username', 'description')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')
    search_fields = ('name', 'email')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Contact, ContactAdmin)
