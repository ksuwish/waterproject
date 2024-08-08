from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum

import json

from .models import Product, Category, Order, OrderItem, User, PersonalInfo, Address
from .forms import ProductForm, CategoryForm, CustomUserCreationForm, PersonalInfoForm, AddressForm, UsernameOnlyForm


def auth_view(request):
    # Save the user and log them in if valid
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('create_personal_info')
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


class CustomLoginView(LoginView):
    # Redirects the user to different dashboards based on their user type after successful login
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
    # Ensure the user is authenticated and a superuser; otherwise, redirect or deny access
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_or_admin_required(view_func):
    # Ensure the user is either staff or a superuser; otherwise, deny access
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")

    return _wrapped_view


@admin_required
def superuser_dashboard(request):
    # Handle product deletion if a POST request with 'delete_product' is received
    if request.method == 'POST' and 'delete_product' in request.POST:
        product_id = request.POST.get('product_id')
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return redirect('superuser_dashboard')

    # Gather data for the dashboard
    products = Product.objects.all()
    orders = Order.objects.all().prefetch_related('items').order_by('-created_at')
    users = User.objects.filter(is_staff=False)

    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=now() - timedelta(days=30)).count()
    new_users = User.objects.filter(date_joined__gte=now() - timedelta(days=30)).count()

    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='completed').count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum']

    total_products = Product.objects.count()
    in_stock_products = Product.objects.filter(stock__gt=0).count()
    out_of_stock_products = Product.objects.filter(stock=0).count()

    today = now().date()
    start_of_month = today.replace(day=1)
    start_of_day = today

    monthly_revenue = \
        Order.objects.filter(status='completed', created_at__gte=start_of_month).aggregate(Sum('total_price'))[
            'total_price__sum']
    daily_revenue = \
        Order.objects.filter(status='completed', created_at__gte=start_of_day).aggregate(Sum('total_price'))[
            'total_price__sum']

    last_month_start = start_of_month - timedelta(days=1)
    last_month_start = last_month_start.replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)

    last_month_revenue = \
        Order.objects.filter(status='completed', created_at__range=[last_month_start, last_month_end]).aggregate(
            Sum('total_price'))['total_price__sum']

    yesterday = today - timedelta(days=1)
    yesterday_revenue = \
        Order.objects.filter(status='completed', created_at__date=yesterday).aggregate(Sum('total_price'))[
            'total_price__sum']

    context = {
        'products': products,
        'orders': orders,
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'new_users': new_users,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'in_stock_products': in_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'monthly_revenue': monthly_revenue,
        'daily_revenue': daily_revenue,
        'last_month_revenue': last_month_revenue,
        'yesterday_revenue': yesterday_revenue,
    }

    return render(request, 'dashboard/superuser_dashboard.html', context)


@staff_or_admin_required
def staff_dashboard(request):
    # Render the staff dashboard page with access restricted to staff or admin users
    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')
    completed_orders = Order.objects.filter(status='completed').prefetch_related('items', 'user')
    return render(request, 'dashboard/staff_dashboard.html', {'pending_orders': pending_orders,
                                                              'completed_orders': completed_orders})


@login_required
def user_dashboard(request):
    # Render the user dashboard page with the user's orders and categories
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    categories = Category.objects.all()

    context = {
        'orders': orders,
        'categories': categories,
    }

    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def order_view(request):
    # Render the order page
    return render(request, 'order.html')


@csrf_exempt
def create_order(request):
    # Process and create a new order based on provided cart data
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            cart_data = data.get('cart', [])
            total_price = data.get('total_price', 0)
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

            order = Order.objects.create(user=user, total_price=total_price)

            for item in cart_data:
                product = Product.objects.get(id=item['product_id'])

                if product.stock < item['quantity']:
                    return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {product.name}'},
                                        status=400)

                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    product_price=item['product_price'],
                    quantity=item['quantity']
                )

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
    # Render the homepage with all categories
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})


@admin_required
def add_product(request):
    # Handle product creation with form submission; redirect to dashboard on success
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('superuser_dashboard')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


@admin_required
def edit_product(request, pk):
    # Handle product update with form submission; redirect to dashboard on success
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('superuser_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})


@admin_required
def user_orders(request, user_id):
    # Display orders for a specific user, ordered by creation date, and render them in the user_orders template
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'admincontent/user_orders.html', {'orders': orders, 'user': user})


@admin_required
def add_category(request):
    # Handle category addition; save the form if valid and redirect to the category list
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'admincontent/add_category.html', {'form': form})


@admin_required
def category_list(request):
    # Display and manage categories; handle form submissions to add new categories
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


@admin_required
def edit_category(request, pk):
    # Edit an existing category; handle form submissions to update category details
    category = Category.objects.get(pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'admincontent/edit_category.html', context)


@admin_required
def delete_category(request, pk):
    # Delete a category after confirming with a POST request, then redirect to the category list
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        category.delete()
    return redirect('category_list')


@login_required
def create_personal_info(request):
    # Create or update personal information for the logged-in user, and redirect to add address page upon success
    try:
        personal_info = PersonalInfo.objects.get(user=request.user)
    except PersonalInfo.DoesNotExist:
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
            return redirect('add_address')
    else:
        form = PersonalInfoForm(instance=personal_info)

    return render(request, 'create_personal_info.html', {'form': form})


@login_required
def add_address_view(request):
    # Handle adding a new address for the logged-in user and redirect to the user dashboard upon success
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
    # Manage and update user's personal and address information, and handle email updates.
    try:
        personal_info = PersonalInfo.objects.get(user=request.user)
    except PersonalInfo.DoesNotExist:
        personal_info = None
    try:
        address_info = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address_info = None

    if request.method == 'POST':
        personal_form = PersonalInfoForm(request.POST, instance=personal_info)
        address_form = AddressForm(request.POST, instance=address_info)
        email = request.POST.get('email', request.user.email)

        if personal_form.is_valid() and address_form.is_valid():
            personal_info = personal_form.save(commit=False)
            personal_info.user = request.user
            personal_info.save()

            request.user.email = email
            request.user.save()

            address_info = address_form.save(commit=False)
            address_info.user = request.user
            address_info.save()

            return redirect('profile_view')

    else:
        personal_form = PersonalInfoForm(instance=personal_info)
        address_form = AddressForm(instance=address_info)

    user_email = request.user.email

    return render(request, 'profile.html', {
        'personal_form': personal_form,
        'address_form': address_form,
        'user_email': user_email
    })


@staff_or_admin_required
def user_detail(request, user_id):
    # Retrieve and display detailed information for a specific user, including personal info, addresses, and orders.
    user = get_object_or_404(User, id=user_id)
    personal_info = get_object_or_404(PersonalInfo, user=user)
    address = Address.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    user_role = 'superuser' if request.user.is_superuser else 'staff'
    return render(request, 'user_detail.html', {
        'user': user,
        'personal_info': personal_info,
        'orders': orders,
        'address': address,
        'user_role': user_role
    })


@login_required
def edit_personal_info(request, user_id):
    # Handle the editing of a user's personal information, updating both the PersonalInfo model and the User model.
    personal_info = get_object_or_404(PersonalInfo, user_id=user_id)
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=personal_info, user=user)
        if form.is_valid():
            form.save()
            user.email = form.cleaned_data['user_email']
            user.save()
            return redirect('user_detail', user_id=user_id)
    else:
        form = PersonalInfoForm(instance=personal_info, user=user)

    return render(request, 'edit_personal_info.html', {'form': form})


def edit_address(request, address_id, user_id):
    # Handle the editing of a user's address information and redirect to the user detail page upon successful update.
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user_detail', user_id=user_id)
    else:
        form = AddressForm(instance=address)
    return render(request, 'edit_address.html', {'form': form, 'user_id': user_id})


@admin_required
def add_user(request):
    # Handle the creation of a new user and associated address, redirecting to the superuser dashboard upon
    # successful addition.
    if request.method == 'POST':
        user_form = UsernameOnlyForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            username = user_form.cleaned_data['username']

            if not User.objects.filter(username=username).exists():
                user = User.objects.create(username=username)

                address = address_form.save(commit=False)
                address.user = user
                address.save()

                return redirect('superuser_dashboard')
            else:
                user_form.add_error('username', 'Username already exists')
    else:
        user_form = UsernameOnlyForm()
        address_form = AddressForm()

    return render(request, 'add_user.html', {'user_form': user_form, 'address_form': address_form})


def mark_order_as_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'completed'
        order.save()
        return redirect('staff_dashboard')  # Güncellenmiş siparişler sayfasına yönlendir
    return redirect('staff_dashboard')


def show_order_map(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    address = Address.objects.filter(user=order.user).first()
    personal_info = PersonalInfo.objects.filter(user=order.user).first()

    context = {
        'address': address,
        'personal_info': personal_info
    }
    return render(request, 'address_view.html', context)


def stock_list(request):
    products = Product.objects.all()
    return render(request, 'stock_list.html', {'products': products})


def last_orders(request):
    # Son siparişleri almak için Order modelini kullan
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'last_orders.html', {'orders': orders})


def user_list(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'users.html', {'users': users})
