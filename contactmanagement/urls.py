from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contactmanagement import views

router = DefaultRouter()
router.register(r'contacts', views.ContactCRUDModelViewSet, basename='contacts')
router.register(r'contact-details-import-export', views.ContactModelViewSet, basename='contact-details-import-export')

urlpatterns = [
    path('', include(router.urls)),
    path('contact-assign/', views.ContactAssignAPIView.as_view(), name="contact-assign"),
    path('contact-remove/', views.ContactRemoveAPIView.as_view(), name="contact-remove"),
]