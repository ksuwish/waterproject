from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
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
        """If the form is valid, redirect the user based on their role."""
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