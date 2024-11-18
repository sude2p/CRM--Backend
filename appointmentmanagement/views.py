from .models import AppointmentDetails
from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from .serializers import AppointmentSerializer
from  core.permissions import FullDjangoModelPermissions, IsAdminOrOrgUser
from rest_framework.permissions import IsAuthenticated, AllowAny



# Create your views here.


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = AppointmentDetails.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminOrOrgUser, FullDjangoModelPermissions, IsAuthenticated]
    # permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    # Filterable fields
    filterset_fields = [
        "appointment_type",  # Filter by appointment type
        "appointment_status",  # Filter by appointment status
        "date",  # Filter by appointment date
        "time",  # Filter by appointment time
    ]

    # Searchable fields
    search_fields = [
        "location",  # Search by location
        "contact__name",  # Assuming 'name' is a field in the Contact model for searching
    ]

    # Orderable fields
    ordering_fields = [
        "date",  # Order by date
        "time",  # Order by time
        "appointment_status",  # Order by appointment status
        "appointment_type",  # Order by appointment type
    ]

    def create(self, request, *args, **kwargs):
        organization_id = request.headers.get("organization")
        serializer = self.get_serializer(data=request.data, context={"organization": organization_id})
        if serializer.is_valid(raise_exception=True):

            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "message": "Appointment created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
            publish_to_rabbitmq("appointment_created",{"appointmentId":serializer.data["id"],
                                                        "organizationId":organization_id,
                                                        "appointmentType":serializer.data["appointment_type"]} )

        else:
            print(serializer.errors)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
      
        return Response(
            {
                "status": "success",
                "message": "Appointments retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "message": "Appointment retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        publish_to_rabbitmq("appointment_updated",{"appointmentId":serializer.data["id"]})
        return Response(
            {
                "status": "success",
                "message": "Appointment updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        publish_to_rabbitmq("appointment_deleted",{"appointmentId":instance.id})
        return Response(
            {"status": "success", "message": "Appointment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
