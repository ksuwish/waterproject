from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    return render(request, "main/index.html")

def blogs(request):
    return render(request, "main/blogs.html")


@login_required
def userpage(request):
    return render(request, "main/userpage.html", {}) 

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html",{"form" :form})