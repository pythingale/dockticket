import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Ticket
from .serializers import TicketSerializer

# Initialize logger
logger = logging.getLogger(__name__)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info("Received ticket creation request with data: %s", request.data)

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error("Validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to create the ticket
            ticket = serializer.save()
            logger.info("Ticket successfully created: %s", ticket)

            # Return the custom success message and ticket details
            response_data = {
                "message": "Ticket successfully created",
                "ticket_code": ticket.unique_code,
                "schedule_date": ticket.day_schedule.date,
                "doctor_id": ticket.day_schedule.doctor.id,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.warning("Validation error during ticket creation: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Unexpected error during ticket creation: %s", str(e))
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
