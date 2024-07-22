from django.urls import path, include
from . import views
from .views import authView

urlpatterns = [
    path("",views.index),
    path("index",views.index),
    path("blogs",views.blogs),
    path("userpage",views.userpage,name='userpage'),
    path("accounts/signup/", authView, name= "authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    
]