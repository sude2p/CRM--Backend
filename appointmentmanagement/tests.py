from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import AppointmentDetails, Contact
from core.models import OrganizationDetail
from contactmanagement.models import Address
from django.contrib.auth.models import User
from core.models import CustomUser
from django.contrib.auth.models import Permission



class AppointmentViewSetTests(APITestCase):
    def setUp(self):
        # Create a test organization
        self.organization = OrganizationDetail.objects.create(ref_org_id=1)

        # Create a test user with permissions
        self.user = CustomUser.objects.create_user(email='test@email.com', password='testpassword')
        self.user.is_staff = True
        self.user.user_permissions.add(
            Permission.objects.get(codename='add_appointmentdetails'),
            Permission.objects.get(codename='change_appointmentdetails'),
            Permission.objects.get(codename='delete_appointmentdetails'),
            Permission.objects.get(codename='view_appointmentdetails'),
        )
        self.user.save()
        
        # Log the user in
        self.client.login(email='test@email.com', password='testpassword')

        # Set the URL for appointments
        self.url = reverse('appointment-list')

        # Create a contact and address for later use
        self.contact = Contact.objects.create(
            full_name="John Doe",
            email="john.doe@example.com",
            phone_mobile="1234567890",
            organization=self.organization
        )
        self.address = Address.objects.create(
            street="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            country="USA"
        )
        self.contact.address = self.address
        self.contact.save()

    def test_crud_appointment(self):
        # Create Appointment
        data = {
            "contact": {
                "full_name": "Alice Smith",
                "email": "alice.smith@example.com",
                "phone_mobile": "5555555555",
                "address": {
                    "street": "789 Maple St",
                    "city": "Newcity",
                    "state": "TX",
                    "zip_code": "67890",
                    "country": "USA"
                }
            },
            "appointment_type": "in_store",
            "appointment_status": "scheduled",
            "location": "Store Location",
            "date": "2024-10-10",
            "time": "10:00:00"
        }
        response = self.client.post(self.url, data, format='json', headers={"organization": "1"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppointmentDetails.objects.count(), 1)

        # Retrieve Appointment
        appointment_id = response.data['data']['id']
        response = self.client.get(reverse('appointment-detail', args=[appointment_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update Appointment
        update_data = {
            "location": "Updated Store Location",
            "appointment_status": "completed"
        }
        response = self.client.patch(reverse('appointment-detail', args=[appointment_id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment = AppointmentDetails.objects.get(id=appointment_id)
        self.assertEqual(appointment.location, "Updated Store Location")
        self.assertEqual(appointment.appointment_status, "completed")

        # Delete Appointment
        response = self.client.delete(reverse('appointment-detail', args=[appointment_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AppointmentDetails.objects.count(), 0)

    def test_no_contact_or_address_creation_on_duplicate(self):
        data = {
            "contact": {
                "full_name": "John Doe",  # Existing contact
                "email": "john.doe@example.com",  # Duplicate email
                "phone_mobile": "1234567890",  # Duplicate phone
                "address": {
                    "street": "456 Elm St",
                    "city": "Othertown",
                    "state": "NY",
                    "zip_code": "67890",
                    "country": "USA"
                }
            },
            "appointment_type": "in_store",
            "appointment_status": "scheduled",
            "location": "Store Location",
            "date": "2024-10-10",
            "time": "10:00:00"
        }

        response = self.client.post(self.url, data, format='json', headers={"organization": "1"})

        # Check that appointment was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppointmentDetails.objects.count(), 1)

        # Check that no new contact or address was created
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Address.objects.count(), 1)

    def test_multiple_appointments_creation(self):
        for i in range(3):
            data = {
                "contact": {
                    "full_name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "phone_mobile": f"12345678{i}",
                    "address": {
                        "street": f"{i} Main St",
                        "city": "Newcity",
                        "state": "TX",
                        "zip_code": f"6789{i}",
                        "country": "USA"
                    }
                },
                "appointment_type": "in_store",
                "appointment_status": "scheduled",
                "location": "Store Location",
                "date": f"2024-10-{10 + i}",
                "time": "10:00:00"
            }

            response = self.client.post(self.url, data, format='json', headers={"organization": "1"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(AppointmentDetails.objects.count(), 3)  # Check 3 appointments created   