import io
import csv
from .models import Contact, Address, Tag, Deal
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from core.renderer import UserRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import views, status
from rest_framework.viewsets import ModelViewSet
from .serializers import (
    ContactAddressSerializer,
    ContactTagSerializer,
    ContactDealSerializer,
    ContactSerializer,
    ContactAssignSerializer,
    ContactRemoveSerializer,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import FullDjangoModelPermissions, IsAdminOrOrgUser
from django.http import HttpResponse
from core.models import CustomUser
from django.db import transaction
from core.publisher import publish_to_rabbitmq


class ContactCRUDModelViewSet(ModelViewSet):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrOrgUser, FullDjangoModelPermissions, IsAuthenticated]
    # permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "company",  # Filter by company
        "status",  # Filter by status (active, inactive, deleted, etc.)
        "industry",  # Filter by industry
        "contact_owner",  # Filter by contact owner (user who owns the contact)
        "shared_with",  # Filter by users the contact is shared with
        "last_contacted_date",  # Filter by the date the contact was last contacted
        "next_follow_up_date",  # Filter by the date of the next follow-up
        "preferred_contact_method",  # Filter by preferred contact method (phone, email, etc.)
        "tags",  # Filter by associated tags
        "birthdate",  # Filter by contact's birthdate
    ]
    search_fields = [
        "full_name",  # Search by full name
        "job_title",  # Search by job title
        "email",  # Search by email
        "phone_work",  # Search by work phone number
        "phone_mobile",  # Search by mobile phone number
        "address__street",  # Search by address street (related Address model)
        "address__city",  # Search by address city (related Address model)
        "address__state",  # Search by address state (related Address model)
        "address__zip_code",  # Search by address zip code (related Address model)
        "notes",  # Search within notes
        "linkedin",  # Search by LinkedIn URL
        "twitter",  # Search by Twitter URL
        "facebook",  # Search by Facebook URL
    ]
    ordering_fields = [
        "full_name",  # Order by full name
        "job_title",  # Order by job title
        "created_at",  # Order by creation date
        "updated_at",  # Order by last updated date
        "last_contacted_date",  # Order by last contacted date
        "next_follow_up_date",  # Order by next follow-up date
        "birthdate",  # Order by birthdate
    ]
    queryset = Contact.objects.all().order_by("id")
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        print(f"Request: {request.data}")

        serializer = self.get_serializer(
            data=request.data, context={"user": request.user, "request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Contact Created Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
            publish_to_rabbitmq("contact_created",{"contactId":serializer.data["id"],
                "contactName":serializer.data["full_name"],
                "contactEmail":serializer.data["email"],
                "contactPhone":serializer.data["phone_mopile"],
                "organizationId":request.headers.get("organization.id")}) # Publish to RabbitMQ
        return Response(
            {
                "status": "error",
                "message": "Contact Creation Error",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def list(self, request, *args, **kwargs):
        print(f"User: {request.user}")
        print(f'Authorization Header: {request.headers.get("Authorization")}')
        print(f"User: {request.user}")
        # print(f'User ID: {request.user_id }')
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Contact Details List",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"status": "success", "message": "Object Found", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        print(f'Authorization Header: {request.headers.get("Authorization")}')
        print(f"User: {request.user}")
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Updated Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
            publish_to_rabbitmq("contact_updated",{"contactId":serializer.data["id"],
                "contactName":serializer.data["full_name"],
                "contactEmail":serializer.data["email"],
                "contactPhone":serializer.data["phone_mopile"],
                "organizationId":request.headers.get("organization.id")}) # Publish to RabbitMQ
            
        return Response(
            {"status": "error", "message": "Update Error", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        print(f'Authorization Header: {request.headers.get("Authorization")}')
        print(f"User: {request.user}")
        instance = self.get_object()
        instance.delete()
        publish_to_rabbitmq("contact_deleted",{"contactId":instance.id})
        return Response(
            {"status": "success", "message": "Deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class ContactModelViewSet(ModelViewSet):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()

    @action(detail=False, methods=["GET"])
    def export_contacts(self, request, *args, **kwargs):
        # Create in-memory output stream
        output = io.StringIO()
        writer = csv.writer(
            output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        # Write the header row
        writer.writerow(
            [
                "full_name",
                "email",
                "phone_work",
                "phone_mobile",
                "lead_source",
                "industry",
                "status",
                "address",
                "tags",
            ]
        )

        # Fetch contacts from database
        contacts = Contact.objects.all()

        for contact in contacts:
            address = (
                f"{contact.address.street}, {contact.address.city}, {contact.address.state}, {contact.address.country}"
                if contact.address
                else ""
            )
            tags = ", ".join(tag.name for tag in contact.tags.all())
            writer.writerow(
                [
                    contact.full_name,
                    contact.email,
                    contact.phone_work,
                    contact.phone_mobile,
                    contact.lead_source,
                    contact.industry,
                    contact.status,
                    address,
                    tags,
                ]
            )

        # Create HTTP response with appropriate headers
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
        return response

    @action(
        detail=False, methods=["POST"], parser_classes=[MultiPartParser, FormParser]
    )
    def import_contacts(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        print(f"File: {file}")
        if not file or not file.name.endswith(".csv"):
            return Response(
                {
                    "status": "error",
                    "message": "Invalid file format. Only CSV files are allowed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        decoded_file = file.read().decode("utf-8").splitlines()

        print(f"Decoded File: {decoded_file}")
        reader = csv.DictReader(decoded_file)

        print(f"Reader: {reader}")
        contacts = []
        for row in reader:
            # Extract address info if present
            address_data = row.get("address", "")
            address_obj = None
            if address_data:
                address_parts = [x.strip() for x in address_data.split(",")]
                if len(address_parts) == 4:
                    address_obj, _ = Address.objects.get_or_create(
                        street=address_parts[0],
                        city=address_parts[1],
                        state=address_parts[2],
                        country=address_parts[3],
                    )

            # Handle tags
            tag_names = row.get("tags", "").split(",")
            tags = [
                Tag.objects.get_or_create(name=tag.strip())[0]
                for tag in tag_names
                if tag.strip()
            ]

            contact = Contact(
                full_name=row["full_name"],
                email=row["email"],
                phone_work=row.get("phone_work"),
                phone_mobile=row.get("phone_mobile"),
                lead_source=row.get("lead_source"),
                industry=row.get("industry"),
                status=row.get("status", "active"),
                address=address_obj,
            )
            contacts.append(contact)

        Contact.objects.bulk_create(contacts)

        # Bulk assign tags after contacts are created
        for contact in contacts:
            contact.tags.set(tags)

        return Response(
            {"status": "success", "message": "Contacts imported successfully."},
            status=status.HTTP_200_OK,
        )


class ContactAssignAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactAssignSerializer(data=request.data)
        if serializer.is_valid():
            contact_ids = serializer.validated_data.get("contact_ids")
            user_ids = serializer.validated_data.get("user_ids")

            contact_objs = Contact.objects.filter(
                id__in=contact_ids, contact_owner=request.user
            )
            if not contact_objs.exists():
                return Response(
                    {
                        "status": "error",
                        "message": "No valid contacts found for assignment.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            user_objs = CustomUser.objects.filter(user_ref_id__in=user_ids)
            if not user_objs.exists():
                return Response(
                    {
                        "status": "error",
                        "message": "No valid users found for assignment.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                with transaction.atomic():
                    for contact in contact_objs:
                        contact.shared_with.add(*user_objs)
                publish_to_rabbitmq("contact_assigned",{"contactId":contact_ids,
                                                        "organizationId":request.headers.get("organization.id")})          
                return Response(
                    {"status": "success", "message": "Contacts assigned successfully."},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "message": f"Contact assignment failed: {str(e)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": "error", "message": "Invalid data."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ContactRemoveAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactRemoveSerializer(data=request.data)
        if serializer.is_valid():
            contact_ids = serializer.validated_data.get("contact_ids")
            user_ids = serializer.validated_data.get("user_ids")

            # Fetch contacts belonging to the current user
            contact_objs = Contact.objects.filter(
                id__in=contact_ids, contact_owner=request.user
            )
            if not contact_objs.exists():
                return Response(
                    {
                        "status": "error",
                        "message": "No valid contacts found for removal.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch users with the given user_ref_id
            user_objs = CustomUser.objects.filter(user_ref_id__in=user_ids)
            if not user_objs.exists():
                return Response(
                    {"status": "error", "message": "No valid users found for removal."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                with transaction.atomic():
                    for contact in contact_objs:
                        contact.shared_with.remove(*user_objs)
               
                publish_to_rabbitmq("contact_removed",{"contactId":contact_ids,
                                                            "organizationId":request.headers.get("organization.id")})    
                return Response(
                    {"status": "success", "message": "Contacts removed successfully."},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Contact removal failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": "error", "message": "Invalid data."},
            status=status.HTTP_400_BAD_REQUEST,
        )
