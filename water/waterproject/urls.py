from django.urls import path, include
from . import views
from .views import authView, CustomLoginView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import user_orders
urlpatterns = [
    path("", views.index),
    path("index", views.index),
    path('blogs/', views.blogs, name='blogs'),
    path("accounts/signup/", authView, name="authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('superuser_dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('order/', views.order_view, name='order'),
    path('create-order/', views.create_order, name='create_order'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('user-orders/<int:user_id>/', user_orders, name='user_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
