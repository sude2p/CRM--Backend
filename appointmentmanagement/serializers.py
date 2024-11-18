from rest_framework import serializers
from django.db import transaction
from contactmanagement.models import Contact, Address
from core.utils import create_googlemeet_link
from core.models import OrganizationDetail
from .models import AppointmentDetails

# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ['id', 'street', 'city', 'state', 'zip_code','country']

# class ContactSerializer(serializers.ModelSerializer):
#     address = AddressSerializer()
#     class Meta:
#         model = Contact
#         fields = ['id', 'full_name', 'email', 'phone_mobile', 'organization', 'address']
#         read_only_fields = ['id']

            
# class AppointmentSerializer(serializers.ModelSerializer):
#     contact = ContactSerializer()
   
#     class Meta:
#         model = AppointmentDetails
#         fields = ["id", "contact", "appointment_type", "appointment_status", "location", "date", "time"]
#         read_only_fields = ["id"]

#     def create(self, validated_data):
#         print(validated_data)
#         try:
#             contact_data = validated_data.pop('contact')
#             address_data = contact_data.pop('address')
#             organization_id = self.context.get("organization")
#             print(f"organization_id is: {organization_id}")
#             email = contact_data.get("email")
#             name = contact_data.get("full_name")
#             contact_number = contact_data.get("phone_mobile")
           
#         except Exception as e:
#             print(e)
#             raise serializers.ValidationError(
#                 {
#                     "status": "error",
#                     "message": "email, name and contact_number are required",
#                 }
#             )

#         try:
            
#             organization_object = OrganizationDetail.objects.get(
#                 ref_org_id=organization_id
                
#             )
#             print(organization_object)
#              # Look for an existing contact
#             if organization_object:
#                 existing_contact = Contact.objects.filter(email=email, organization=organization_object, 
#                                            phone_mobile=contact_number,full_name=name).first()
             
#                 if existing_contact is None:
                    
#                     with transaction.atomic():
#                         contact_obj = Contact.objects.create(full_name = name, email=email , phone_mobile=contact_number,
#                                                              organization=organization_object)
                            
#                         address_obj = Address.objects.create(**address_data )
#                         contact_obj.address = address_obj
#                         contact_obj.save()

#             else:
#                 contact_obj = existing_contact # Use the existing contact
#                 # Check if the existing address matches
#                 existing_address = contact_obj.address
#                 if existing_address:
#                     if address_data != existing_address:
#                         # Update the address
#                         with transaction.atomic():
#                             existing_address.street = address_data.get('street', existing_address.street)
#                             existing_address.city = address_data.get('city', existing_address.city)
#                             existing_address.state = address_data.get('state', existing_address.state)
#                             existing_address.zip_code = address_data.get('zip_code', existing_address.zip_code)
#                             existing_address.country = address_data.get('country', existing_address.country)
#                             existing_address.save()
               
#                 else:
#                     # Create a new address
#                     with transaction.atomic():
#                         address_obj = Address.objects.create(**address_data )
#                         contact_obj.address = address_obj
#                         contact_obj.save()
#         except OrganizationDetail.DoesNotExist:
#             raise serializers.ValidationError({"status": "error", "message": "Organization not found"})        
#         except Exception as e:
#             print(e)
#             raise serializers.ValidationError(
#                 {"status": "error", "message": "Duplicate contact found Error creating contact"}
#             )

#         # create the appointment based on appointment_type
#         try:
#             with transaction.atomic():
#                 appointment_type = validated_data.get("appointment_type")
#                 appointment_status = validated_data.get(
#                     "appointment_status", "scheduled"
#                 )
#                 # Create appointment
                
#                 appointment_obj = AppointmentDetails.objects.create(
#                     contact=contact_obj,
#                     appointment_status=appointment_status,
#                     appointment_type=appointment_type,
#                     date=validated_data.get("date"),
#                     time=validated_data.get("time"),
#                     location=validated_data.get("location"),
#                     # **validated_data
#                 )

#                 if appointment_type == "online":
#                     appointment_obj.location = create_googlemeet_link(appointment_obj)

#                 elif appointment_type == "in_store":
#                     appointment_obj.location = (
#                         "in_store"  # give the google map location of the
#                     )

#                 elif appointment_type == "on_site":
#                     appointment_obj.location = str(contact_obj.address)

#                 appointment_obj.save()

#         except Exception as e:
#             print(e)
#             raise serializers.ValidationError(
#                 {"status": "error", "message": "Error creating appointment"}
#             )
#         return appointment_obj




class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code', 'country']

class ContactSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'email', 'phone_mobile', 'organization', 'address']
        read_only_fields = ['id']
        ref_name="AppointmentContactSerializer"
        
    # def validate_email(self,value):
    #     if not value:
    #         raise serializers.ValidationError("Email is required")
    #     if Contact.objects.filter(email=value).exists():
    #         raise serializers.ValidationError("Contact with this Email already exists")
    #     return value


class AppointmentSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = AppointmentDetails
        fields = ["id", "contact", "appointment_type", "appointment_status", "location", "date", "time"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        print(validated_data)
        try:
            contact_data = validated_data.pop('contact')
            address_data = contact_data.pop('address')
            organization_id = self.context.get("organization")
            print(f"organization_id is: {organization_id}")
            email = contact_data.get("email")
            name = contact_data.get("full_name")
            contact_number = contact_data.get("phone_mobile")

            # Check for existing organization
            organization_object = OrganizationDetail.objects.get(ref_org_id=organization_id)
            print(organization_object)
            # Look for an existing contact
            print(f"Querying with email: '{email}', phone: '{contact_number}', organization: '{organization_object}', full name: '{name}'")
            existing_contact = Contact.objects.filter(
                email__iexact=email,
                phone_mobile__iexact=contact_number,
                organization__exact=organization_object,
                full_name__iexact=name
            ).first()
            # print(f"existing_contact query: {existing_contact.query}")
            print(f"existing_contact result: {existing_contact}")

            if existing_contact:
                print(f"existing_contact found: {existing_contact}")
            else:
                print("No existing contact found.")
                        
                print(f"existing_contact is: {existing_contact}")


            if existing_contact is not None:
                print(f"existing_contact_to_not_create_ is: {existing_contact}")
                contact_obj = existing_contact
                # Check if the existing address matches
                existing_address = contact_obj.address
                if existing_address:
                    if (existing_address.street != address_data['street'] or
                        existing_address.city != address_data['city'] or
                        existing_address.state != address_data['state'] or
                        existing_address.zip_code != address_data['zip_code'] or
                        existing_address.country != address_data['country']):
                        # Update existing address
                        with transaction.atomic():
                            existing_address.street = address_data['street']
                            existing_address.city = address_data['city']
                            existing_address.state = address_data['state']
                            existing_address.zip_code = address_data['zip_code']
                            existing_address.country = address_data['country']
                            existing_address.save()
                else:
                    # Create new address if none exists for the existing contact
                    with transaction.atomic():
                        new_address = Address.objects.create(**address_data)
                        contact_obj.address = new_address
                        contact_obj.save()

            else:
                # Create new contact since no existing contact is found
                with transaction.atomic():
                    contact_obj = Contact.objects.create(
                        full_name=name,
                        email=email,
                        phone_mobile=contact_number,
                        organization=organization_object,
                        source="chatbot",
                    )
                    address_obj = Address.objects.create(**address_data)
                    contact_obj.address = address_obj
                    contact_obj.save()

        except OrganizationDetail.DoesNotExist:
            raise serializers.ValidationError({"status": "error", "message": "Organization not found"})
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                {"status": "error", "message": "Error creating contact"}
            )

        # Create the appointment based on appointment_type
        try:
            with transaction.atomic():
                appointment_type = validated_data.get("appointment_type")
                appointment_status = validated_data.get("appointment_status", "scheduled")

                appointment_obj = AppointmentDetails.objects.create(
                    contact=contact_obj,
                    appointment_status=appointment_status,
                    appointment_type=appointment_type,
                    date=validated_data.get("date"),
                    time=validated_data.get("time"),
                    location=validated_data.get("location"),
                )

                # Set location based on appointment type
                if appointment_type == "online":
                    appointment_obj.location = create_googlemeet_link(appointment_obj)
                elif appointment_type == "in_store":
                    appointment_obj.location = "in_store"
                elif appointment_type == "on_site":
                    appointment_obj.location = str(contact_obj.address)

                appointment_obj.save()

        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                {"status": "error", "message": "Error creating appointment"}
            )

        return appointment_obj