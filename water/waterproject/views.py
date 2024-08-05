from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, timedelta
from django.db.models import Sum
import json

from .models import Product, Category, Order, OrderItem, User, PersonalInfo, Address
from .forms import ProductForm, CategoryForm, CustomUserCreationForm, PersonalInfoForm, AddressForm, UsernameOnlyForm


# Create your views here.


def index(request):
    return render(request, "main/index.html")


def blogs(request):
    return render(request, "main/blogs.html")


def authView(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Yeni kullanıcıyı kaydet
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')  # Kullanıcı formundaki şifre alanını kontrol edin
            # Kullanıcıyı doğrula
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Kullanıcıyı giriş yaptır
                return redirect('create_personal_info')
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


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


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_or_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            # Yetkisiz kullanıcıları bir hata sayfasına veya ana sayfaya yönlendirebilirsiniz.

            return HttpResponseForbidden("You do not have permission to access this page.")

    return _wrapped_view


@admin_required
def superuser_dashboard(request):
    # Ürün silme işlemi
    if request.method == 'POST' and 'delete_product' in request.POST:
        product_id = request.POST.get('product_id')
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return redirect('superuser_dashboard')

    # Ürünleri ve diğer verileri al
    products = Product.objects.all()
    orders = Order.objects.all().prefetch_related('items').order_by('-created_at')
    users = User.objects.filter(is_staff=False)

    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=now() - timedelta(days=30)).count()
    new_users = User.objects.filter(date_joined__gte=now() - timedelta(days=30)).count()

    total_orders = Order.objects.count()
    # completed_orders = Order.objects.filter(status='completed').count()
    # pending_orders = Order.objects.filter(status='pending').count()
    # total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum']

    total_products = Product.objects.count()
    in_stock_products = Product.objects.filter(stock__gt=0).count()
    out_of_stock_products = Product.objects.filter(stock=0).count()

    context = {
        'products': products,
        'orders': orders,
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'new_users': new_users,
        'total_orders': total_orders,
        # 'completed_orders': completed_orders,
        # 'pending_orders': pending_orders,
        # 'total_revenue': total_revenue,
        'total_products': total_products,
        'in_stock_products': in_stock_products,
        'out_of_stock_products': out_of_stock_products,
    }

    return render(request, 'dashboard/superuser_dashboard.html', context)


@staff_or_admin_required
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


@csrf_exempt
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

            # Siparişe ürünleri ekle ve stokları güncelle
            for item in cart_data:
                product = Product.objects.get(id=item['product_id'])

                if product.stock < item['quantity']:
                    return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {product.name}'}, status=400)

                # Siparişe ürün ekle
                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    product_price=item['product_price'],
                    quantity=item['quantity']
                )

                # Stokları güncelle
                product.stock -= item['quantity']
                product.save()

            return JsonResponse({'status': 'success', 'order_id': order.id})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def index(request):
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'dashboard/superuser_dashboard.html', {'products': products})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('superuser_dashboard')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('superuser_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})


def user_orders(request, user_id):
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')  # Kullanıcının siparişlerini getir
    return render(request, 'admincontent/user_orders.html', {'orders': orders, 'user': user})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # URL adı 'superuser_dashboard' olmalı
    else:
        form = CategoryForm()
    return render(request, 'admincontent/add_category.html', {'form': form})


def category_list(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()

    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'admincontent/category_list.html', context)


def edit_category(request, pk):
    category = Category.objects.get(pk=pk)
    if request.method == 'POST':
        # Formu POST verileri ve dosyalar ile oluştur
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        # Formu sadece model örneği ile oluştur
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'admincontent/edit_category.html', context)


def delete_category(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        category.delete()
    return redirect('category_list')


@login_required
def create_personal_info(request):
    try:
        # Mevcut kullanıcının PersonalInfo kaydını al
        personal_info = PersonalInfo.objects.get(user=request.user)
    except PersonalInfo.DoesNotExist:
        # PersonalInfo kaydı yoksa, yeni bir nesne oluştur
        personal_info = PersonalInfo(
            user=request.user,
            name=request.user.first_name,
            surname=request.user.last_name,
            phone=request.user.userprofile.phone_number if hasattr(request.user, 'userprofile') else ''
        )

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=personal_info)
        if form.is_valid():
            form.save()
            return redirect('add_address')  # Başarılı işlem sonrası yönlendirme yapabilirsiniz
    else:
        form = PersonalInfoForm(instance=personal_info)

    return render(request, 'create_personal_info.html', {'form': form})


@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('user_dashboard')
    else:
        form = AddressForm()

    return render(request, 'add_address.html', {'form': form})


@login_required
def profile_view(request):
    try:
        # Mevcut kullanıcının PersonalInfo kaydını al
        personal_info = PersonalInfo.objects.get(user=request.user)
    except PersonalInfo.DoesNotExist:
        personal_info = None

    try:
        # Mevcut kullanıcının AddressInfo kaydını al
        address_info = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address_info = None

    if request.method == 'POST':
        # POST verileriyle formları başlat
        personal_form = PersonalInfoForm(request.POST, instance=personal_info)
        address_form = AddressForm(request.POST, instance=address_info)

        # Kullanıcıdan gelen email adresini al
        email = request.POST.get('email', request.user.email)

        if personal_form.is_valid() and address_form.is_valid():
            # Kişisel bilgileri kaydet
            personal_info = personal_form.save(commit=False)
            personal_info.user = request.user
            personal_info.save()

            # Kullanıcının email adresini güncelle
            request.user.email = email
            request.user.save()

            # Adres bilgilerini kaydet
            address_info = address_form.save(commit=False)
            address_info.user = request.user
            address_info.save()

            return redirect('profile_view')

    else:
        # GET isteğinde mevcut bilgileri formlara yükle
        personal_form = PersonalInfoForm(instance=personal_info)
        address_form = AddressForm(instance=address_info)

    user_email = request.user.email

    return render(request, 'profile.html', {
        'personal_form': personal_form,
        'address_form': address_form,
        'user_email': user_email
    })


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    personal_info = get_object_or_404(PersonalInfo, user=user)
    address = Address.objects.filter(user=user)  # Kullanıcıya ait adresleri al
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'user_detail.html', {
        'user': user,
        'personal_info': personal_info,
        'orders': orders,
        'address': address
    })


@login_required
def edit_personal_info(request, user_id):
    personal_info = get_object_or_404(PersonalInfo, user_id=user_id)
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=personal_info, user=user)
        if form.is_valid():
            form.save()
            user.email = form.cleaned_data['user_email']
            user.save()
            return redirect('user_detail', user_id=user_id)  # Yönlendirme yapacağınız sayfa
    else:
        form = PersonalInfoForm(instance=personal_info, user=user)

    return render(request, 'edit_personal_info.html', {'form': form})


def edit_address(request, address_id, user_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user_detail', user_id=user_id)  # Kullanıcı detay sayfasına yönlendir
    else:
        form = AddressForm(instance=address)
    return render(request, 'edit_address.html', {'form': form, 'user_id': user_id})


def add_user(request):
    if request.method == 'POST':
        user_form = UsernameOnlyForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            username = user_form.cleaned_data['username']

            if not User.objects.filter(username=username).exists():
                user = User.objects.create(username=username)

                # Adres bilgilerini kaydet
                address = address_form.save(commit=False)
                address.user = user  # Adresin kullanıcıya ait olduğunu belirtin
                address.save()

                return redirect('superuser_dashboard')  # Başarıyla ekledikten sonra yönlendirme
            else:
                user_form.add_error('username', 'Username already exists')
    else:
        user_form = UsernameOnlyForm()
        address_form = AddressForm()

    return render(request, 'add_user.html', {'user_form': user_form, 'address_form': address_form})
