from django.shortcuts import render

def index_page(request):
    return render(request,"website/index.html")

def blog_page(request):
    return render(request,"website/blog.html")

def blog_single_page(request):
    return render(request,"website/blog_single.html")

def contact_page(request):
    return render(request,"website/contact.html")

def services_page(request):
    return render(request,"website/services.html")

def doctors_page(request):
    return render(request,"website/doctors.html")

def about_page(request):
    return render(request,"website/about.html")

def navigation(request):
    return render(request,"website/navigation.html")