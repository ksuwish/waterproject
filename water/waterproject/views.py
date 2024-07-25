from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
from .models import Product, Category, Order, OrderItem, Product
# Create your views here.

def index(request):
    return render(request, "main/index.html")

def blogs(request):
    return render(request, "main/blogs.html")

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html",{"form" :form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.is_superuser:
            return redirect(reverse_lazy('superuser_dashboard'))
        elif user.is_staff:
            return redirect(reverse_lazy('staff_dashboard'))
        else:
            return redirect(reverse_lazy('user_dashboard'))



@login_required
def superuser_dashboard(request):
    return render(request, 'dashboard/superuser_dashboard.html')

@login_required
def staff_dashboard(request):
    return render(request, 'dashboard/staff_dashboard.html')

@login_required
def user_dashboard(request):
    return render(request, 'dashboard/user_dashboard.html')

def blogs(request):
    mineralwater_category = Category.objects.get(name='mineralwater')
    products = Product.objects.filter(category=mineralwater_category)
    return render(request, 'blogs.html', {'products': products})

def user_dashboard(request):
    # Kategorileri al
    categories = Category.objects.all()
    
    # Her kategori için ürünleri filtrele
    context = {
        'categories': categories,
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)


def order_view(request):
    return render(request, 'order.html')


def create_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        if not cart:
            return redirect('home')  # Sepet boşsa ana sayfaya yönlendir

        total_price = 0
        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart:
            product = Product.objects.get(id=item['id'])  # Ürünü `Product` modelinden al
            item_price = product.price * item['quantity']  # Toplam fiyatı hesapla
            total_price += item_price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=product.price
            )

        # Toplam fiyatı güncelle
        order.total_price = total_price
        order.save()

        request.session['cart'] = []  # Sepeti temizle
        return redirect('order_success')  # Sipariş başarılı sayfasına yönlendir

    return render(request, 'order.html')

