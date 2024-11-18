from django.contrib import admin
from django.urls import path, include
from .views import handle_role_created

urlpatterns = [
    
    path('roles-permissions/',handle_role_created, name="roles-permissions"),
    
]
