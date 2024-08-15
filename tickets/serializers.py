from datetime import timedelta

from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework import serializers

from .models import DaySchedule
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ticket
        fields = ["user_id", "doctor_id", "unique_code"]

    def validate_user_id(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("user_id must be an integer.")
        return value

    def validate_doctor_id(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("doctor_id must be an integer.")
        return value

    def create(self, validated_data):
        user_id = validated_data.get("user_id")
        doctor_id = validated_data.get("doctor_id")
        today = now().date()
        end_of_week = today + timedelta(days=(7 - today.weekday()))

        # Get all DaySchedules for the doctor in the current week
        week_schedules = DaySchedule.objects.filter(
            doctor_id=doctor_id,
            date__range=[today, end_of_week],
        ).order_by("date")

        if not week_schedules.exists():
            raise serializers.ValidationError("No available schedules for this doctor this week.")

        # Iterate over the days in the week to find an available slot
        for schedule in week_schedules:
            if len(schedule.patients) < schedule.max_patients:
                # If there's availability, add the patient and create the ticket
                schedule.patients.append(user_id)
                schedule.save()

                # Create the ticket
                ticket = Ticket.objects.create(day_schedule=schedule, user_id=user_id, unique_code=get_random_string(20))
                return ticket

        # If no slots are available for the current week
        raise serializers.ValidationError("No available slots for this doctor this week.")
