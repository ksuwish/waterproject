from django.urls import path, include
from . import views
from .views import authView, CustomLoginView

urlpatterns = [
    path("",views.index),
    path("index",views.index),
    path("blogs",views.blogs),
    path("accounts/signup/", authView, name= "authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('superuser_dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
]
