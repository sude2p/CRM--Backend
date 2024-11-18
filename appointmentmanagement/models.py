from django.db import models
from contactmanagement.models import Contact


# Create your models here.
class AppointmentDetails(models.Model):

    APPOINTMENT_TYPE_CHOICES = [
        ("online", "Online"),
        ("in_store", "In-Store"),
        ("on_site", "On-Site"),
    ]

    APPOINTMENT_STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    contact = models.ForeignKey('contactmanagement.Contact',
         on_delete=models.CASCADE, related_name="appointments"
    )
    appointment_type = models.CharField(
        max_length=100, choices=APPOINTMENT_TYPE_CHOICES
    )
    appointment_status = models.CharField(
        max_length=100, choices=APPOINTMENT_STATUS_CHOICES
    )
    location = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.contact.full_name
