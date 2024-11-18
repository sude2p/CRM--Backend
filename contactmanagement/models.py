from django.db import models
from encrypted_model_fields.fields import (
    EncryptedCharField,
    EncryptedEmailField,
    EncryptedTextField,
)
from auditlog.registry import auditlog
from core.models import CustomUser, OrganizationDetail


class Contact(models.Model):
    INDUSTRY_CHOICES = [
        ("agriculture", "Agriculture"),
        ("banking", "Banking"),
        ("construction", "Construction"),
        ("education", "Education"),
        ("finance", "Finance"),
        ("healthcare", "Healthcare"),
        ("manufacturing", "Manufacturing"),
        ("retail", "Retail"),
        ("transportation", "Transportation"),
        ("technology", "Technology"),
        ("telecom", "Telecom"),
        ("travel", "Travel"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("deleted", "Deleted"),
        ("Prospect", "Prospect"),
    ]

    CONTACT_METHOD_CHOICES = [
        ("phone", "Phone"),
        ("email", "Email"),
        ("chat", "Chat"),
        ("sms", "SMS"),
        ("other", "Other"),
    ]

    # Basic information
    full_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    source = models.CharField(
        max_length=100, blank=True, null=True, default="chatbot"
    )  # not available in FE
    phone_work = models.CharField(max_length=20, blank=True, null=True)
    phone_mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    organization = models.ForeignKey(
        OrganizationDetail, on_delete=models.SET_NULL, blank=True, null=True
    )
    # Address (related to Address model)
    address = models.OneToOneField(
        "Address", on_delete=models.CASCADE, blank=True, null=True
    )
    birthdate = models.DateField(null=True, blank=True)

    # Other contact details for Industry.
    lead_source = models.CharField(
        max_length=100, blank=True, null=True
    )  # not available in FE
    company = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(
        max_length=100, choices=INDUSTRY_CHOICES, blank=True, null=True
    )
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, blank=True, null=True, default="active"
    )
    # Ownership & communication
    contact_owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owned_contacts",
    )
    shared_with = models.ManyToManyField(CustomUser, blank=True)  # not available in FE
    last_contacted_date = models.DateField(blank=True, null=True)
    next_follow_up_date = models.DateField(blank=True, null=True)
    preferred_contact_method = models.CharField(
        max_length=100, choices=CONTACT_METHOD_CHOICES, blank=True, null=True
    )

    notes = EncryptedTextField(blank=True, null=True)
    # Social media
    linkedin = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    # Tags
    tags = models.ManyToManyField("Tag", blank=True)

    # Dates and custom fields
    custom_fields = models.JSONField(null=True, blank=True)  # not available in FE

    # Deal/Opportunity association (Many-to-Many)
    deals = models.ManyToManyField("Deal", blank=True)  # not available in FE

    def __str__(self):
        return self.full_name


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country}"


class Deal(models.Model):
    DEAL_STAGE_CHOICES = [
        ("negotiation", "Negotiation"),
        ("proposal sent", "Proposal Sent"),
        ("closed won", "Closed Won"),
        ("closed lost", "Closed Lost"),
        ("on hold", "On Hold"),
    ]

    DEAL_STATUS_CHOICES = [("won", "Won"), ("lost", "Lost"), ("open", "Open")]

    title = models.CharField(max_length=100)
    value = models.DecimalField(
        max_digits=12, decimal_places=2
    )  # Deal value, e.g., $50,000
    stage = models.CharField(max_length=100, choices=DEAL_STAGE_CHOICES)
    close_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=100, choices=DEAL_STATUS_CHOICES, default="open"
    )

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


auditlog.register(Contact)
