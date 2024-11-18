from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from appointmentmanagement import views

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')




urlpatterns = [
    path('', include(router.urls)),
  
    
]
