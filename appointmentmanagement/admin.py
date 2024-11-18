from django.contrib import admin
from .models import AppointmentDetails

# Register your models here.

class AppointmentDetailsAdmin(admin.ModelAdmin):
    list_display = ('contact', 'appointment_type', 'appointment_status', 'date', 'time')
    list_filter = ('appointment_type', 'appointment_status', 'date')
    search_fields = ('contact__full_name',)  # Assuming Contact model has a name field
    ordering = ('date', 'time')
    date_hierarchy = 'date'
    
    # Optional: Customize form fields in the admin
    fieldsets = (
        (None, {
            'fields': ('contact', 'appointment_type', 'appointment_status', 'location', 'date', 'time')
        }),
    )
    
    # Optional: Make certain fields read-only in the admin
    def get_readonly_fields(self, request, obj=None):
        if obj:  # When editing an existing appointment
            return ['contact', 'appointment_type', 'date']  # Example fields to make read-only
        return super().get_readonly_fields(request, obj)

# Register the model and admin class
admin.site.register(AppointmentDetails, AppointmentDetailsAdmin)