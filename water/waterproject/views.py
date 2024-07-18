from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "main/index.html")

def blogs(request):
    return render(request, "main/blogs.html")

def blog_details(request, id):
    return render(request, "main/blog-details.html", {"id" : id}) 