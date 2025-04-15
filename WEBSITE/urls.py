from django.urls import path,include
from . import views
# from SUPERADMIN.views import SuperAdminLoginView
# from DOCTOR.views import DoctorLoginView
# from RECEPTION.views import ReceptionLoginView
from .views import navigation

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('blogs/', views.blog_page, name='blog_page'),
    path('blog-single/', views.blog_single_page, name='blog_single_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('doctors/', views.doctors_page, name='doctors_page'),
    path('services/', views.services_page, name='services_page'),
    path('about/', views.about_page, name='about_page'),
    # path('superadmin_login/', SuperAdminLoginView.as_view(), name='superadminloginview'),
    # path('reception-login/', ReceptionLoginView.as_view(), name='reception-login'),
    # path('login/', DoctorLoginView.as_view(), name='doctor-login'),
    path('navigation/', navigation, name='navigation'),
]