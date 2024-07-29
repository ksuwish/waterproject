from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
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



def blogs(request):
    mineralwater_category = Category.objects.get(name='mineralwater')
    products = Product.objects.filter(category=mineralwater_category)
    return render(request, 'blogs.html', {'products': products})

@login_required
def user_dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'orders': orders,
        'categories': categories,
    }

    
    
    return render(request, 'dashboard/user_dashboard.html', context)


def order_view(request):
    return render(request, 'order.html')


@csrf_exempt  # Eğer CSRF korumasını devre dışı bırakmak istiyorsanız, kullanabilirsiniz.
def create_order(request):
    if request.method == 'POST':
        try:
            # Sipariş verilerini al
            data = json.loads(request.body.decode('utf-8'))
            cart_data = data.get('cart', [])
            total_price = data.get('total_price', 0)

            # Kullanıcıyı al
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

            # Yeni siparişi oluştur
            order = Order.objects.create(user=user, total_price=total_price)

            # Siparişe ürünleri ekle
            for item in cart_data:
                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    product_price=item['product_price'],
                    quantity=item['quantity']
                )

            return JsonResponse({'status': 'success', 'order_id': order.id})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

