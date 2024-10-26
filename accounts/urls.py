# accounts/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
]

