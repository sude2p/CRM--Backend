from rest_framework import serializers
from .models import Contact, Address, Deal, Tag
from django.db import transaction


class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "street", "city", "state", "zip_code"]


class ContactDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["id", "title", "value", "stage", "close_date", "owner", "status"]


class ContactTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ContactSerializer(serializers.ModelSerializer):
    address = ContactAddressSerializer(required=False, read_only=True)
    tags = ContactTagSerializer(many=True, required=False,read_only=True)
    deals = ContactDealSerializer(many=True,read_only=True)
    class Meta:
        model = Contact
        fields = ["full_name","email", "phone_mobile","source", "tags", "deals", "address"]
        ref_name = "ContactManagementContactSerializer"

    def create(self, validated_data):
        # Extract the shared_with data and remove it from validated_data
        shared_with = validated_data.pop("shared_with", [])
        address_data = validated_data.pop("address", None)
        tags_data = validated_data.pop("tags", [])
        deals_data = validated_data.pop("deals", [])
        user = self.context["user"]
        request = self.context.get("request")
        # Check if request.user exists, otherwise set source as 'chatbot'
        if user and hasattr(request, "email"):
            source = request.email
            contact_owner = user
        else:
            source = "chatbot"
            contact_owner = None

        # Assign the contact_owner and source fields
        validated_data["contact_owner"] = contact_owner
        validated_data["source"] = source
        try:
            with transaction.atomic():
                # Create the Contact object
                contact_obj = Contact.objects.create(**validated_data)
                # Handle address
                if address_data:
                    address_serializer = ContactAddressSerializer(data=address_data)
                    address_serializer.is_valid(raise_exception=True)
                    address = address_serializer.save()
                    contact_obj.address = address
                    contact_obj.save()

                # Assign the many-to-many relationship using the set() method
                # Assign many-to-many relationships (assuming IDs are provided)
                if tags_data:
                    tags = [
                        Tag.objects.get_or_create(**tag_data)[0]
                        for tag_data in tags_data
                    ]
                    contact_obj.tags.set(tags)

                if deals_data:
                    deals = [
                        Deal.objects.get_or_create(**deal_data)[0]
                        for deal_data in deals_data
                    ]
                    contact_obj.deals.set(deals)

                    # Handle shared_with many-to-many field
                    contact_obj.shared_with.set(shared_with)

                return contact_obj

        except Exception as e:
            # Handle exceptions (optional: log the error or raise a specific error)
            raise serializers.ValidationError(
                f"Error occurred while creating contact: {str(e)}"
            )

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        tags_data = validated_data.pop("tags", [])
        deals_data = validated_data.pop("deals", [])

        # Update address
        if address_data:
            address_serializer = ContactAddressSerializer(
                instance.address, data=address_data, partial=True
            )
            if address_serializer.is_valid():
                address = address_serializer.save()
                instance.address = address

        if tags_data:
            tag_instances = [
                Tag.objects.get_or_create(**tag_data)[0] for tag_data in tags_data
            ]
            instance.tags.set(tag_instances)

        # Update deals
        if deals_data:
            deal_instances = [
                Deal.objects.get_or_create(**deal_data)[0] for deal_data in deals_data
            ]
            instance.deals.set(deal_instances)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ContactAssignSerializer(serializers.Serializer):
    contact_ids = serializers.ListField(child=serializers.IntegerField())
    user_ids = serializers.ListField(child=serializers.IntegerField())


class ContactRemoveSerializer(serializers.Serializer):
    contact_ids = serializers.ListField(child=serializers.IntegerField())
    user_ids = serializers.ListField(child=serializers.IntegerField())
