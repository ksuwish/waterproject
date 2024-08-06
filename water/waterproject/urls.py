from django.urls import path, include
from . import views
from .views import auth_view, CustomLoginView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import user_orders, create_personal_info, add_address_view

urlpatterns = [
    path("", views.index),
    path("accounts/signup/", auth_view, name="authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('superuser_dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('order/', views.order_view, name='order'),
    path('create-order/', views.create_order, name='create_order'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('user-orders/<int:user_id>/', user_orders, name='user_orders'),
    path('add-category/', views.add_category, name='add_category'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('create-personal-info/', create_personal_info, name='create_personal_info'),
    path('add-address/', add_address_view, name='add_address'),
    path('profile/', views.profile_view, name='profile_view'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('edit_personal_info/<int:user_id>/', views.edit_personal_info, name='edit_personal_info'),
    path('edit-address/<int:user_id>/<int:address_id>/', views.edit_address, name='edit_address'),
    path('add_user/', views.add_user, name='add_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
