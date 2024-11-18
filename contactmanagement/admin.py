# from django.contrib import admin
# from .models import Contact, Address, Deal, Tag

# # Custom admin for Contact model
# class ContactAdmin(admin.ModelAdmin):
#     # Fields to display in the list view
#     list_display = (
#         "full_name", 
#         "job_title", 
#         "organization", 
#         "email", 
#         "phone_work", 
#         "status", 
#         "contact_owner", 
#         "last_contacted_date", 
#         "next_follow_up_date"
#     )
    
#     # Fields to search in the admin search bar
#     search_fields = ("full_name", "email", "phone_work", "phone_mobile", "organization__name")
    
#     # Filters on the right-hand side
#     list_filter = ("industry", "status", "contact_owner", "preferred_contact_method", "last_contacted_date")
    
#     # Fields to display in the form (detail view)
#     fieldsets = (
#         ("Basic Information", {
#             "fields": ("full_name", "job_title", "organization", "email", "phone_work", "phone_mobile", "address")
#         }),
#         ("Additional Details", {
#             "fields": ("lead_source", "industry", "status", "notes", "tags")
#         }),
#         ("Ownership & Communication", {
#             "fields": ("contact_owner", "shared_with", "last_contacted_date", "next_follow_up_date", "preferred_contact_method")
#         }),
#         ("Social Media", {
#             "fields": ("linkedin", "twitter", "facebook")
#         }),
#         ("Custom Fields", {
#             "fields": ("birthdate", "custom_fields")
#         }),
#         ("Deal/Opportunity", {
#             "fields": ("deals",)
#         }),
#     )
    
#     # Add inline editing for many-to-many and related fields
#     filter_horizontal = ("shared_with", "tags", "deals")

#     # Specify read-only fields if needed
#     readonly_fields = ("last_contacted_date", "next_follow_up_date")

# # Register the models with the custom admin class
# admin.site.register(Contact, ContactAdmin)
# admin.site.register(Address)
# admin.site.register(Deal)
# admin.site.register(Tag)


from django.contrib import admin
from .models import Contact, Address, Deal, Tag

# Custom admin for Contact model
class ContactAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        "id",
        "full_name", 
        "job_title", 
        "company",   
        "email", 
        "phone_mobile",
        "phone_work", 
        "status", 
        "contact_owner", 
        "last_contacted_date", 
        "next_follow_up_date"
    )
    
    # Fields to search in the admin search bar
    search_fields = ("full_name", "email", "phone_work", "phone_mobile", "company")
    
    # Filters on the right-hand side
    list_filter = ("industry", "status", "contact_owner", "preferred_contact_method", "last_contacted_date","organization")
    
    # Fields to display in the form (detail view)
    fieldsets = (
        ("Basic Information", {
            "fields": ("full_name", "job_title", "company", "email", "phone_work", "phone_mobile", "address","organization")
        }),
        ("Additional Details", {
            "fields": ("lead_source", "industry", "status", "notes", "tags")
        }),
        ("Ownership & Communication", {
            "fields": ("contact_owner", "shared_with", "last_contacted_date", "next_follow_up_date", "preferred_contact_method")
        }),
        ("Social Media", {
            "fields": ("linkedin", "twitter", "facebook")
        }),
        ("Custom Fields", {
            "fields": ("birthdate", "custom_fields")
        }),
        ("Deal/Opportunity", {
            "fields": ("deals",)
        }),
    )
    
    # Add inline editing for many-to-many and related fields
    filter_horizontal = ("shared_with", "tags", "deals")

    # Specify read-only fields if needed
    readonly_fields = ("last_contacted_date", "next_follow_up_date")

    # Add actions to the admin for bulk updates
    actions = ['mark_as_inactive', 'mark_as_deleted']

    # Define custom actions
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
        self.message_user(request, f"{queryset.count()} contacts marked as inactive.")

    def mark_as_deleted(self, request, queryset):
        queryset.update(status='deleted')
        self.message_user(request, f"{queryset.count()} contacts marked as deleted.")

    mark_as_inactive.short_description = "Mark selected contacts as inactive"
    mark_as_deleted.short_description = "Mark selected contacts as deleted"

# Custom admin for Address model
class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "state", "zip_code", "country")
    search_fields = ("street", "city", "state", "zip_code", "country")

# Custom admin for Deal model
class DealAdmin(admin.ModelAdmin):
    list_display = ("title", "value", "stage", "close_date", "owner", "status")
    search_fields = ("title", "owner__username", "status")
    list_filter = ("stage", "status", "close_date")

# Custom admin for Tag model
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    


# Register the models with the custom admin class
admin.site.register(Contact, ContactAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Deal, DealAdmin)
admin.site.register(Tag, TagAdmin)