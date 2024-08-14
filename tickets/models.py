from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

from doctors.models import DaySchedule


class Ticket(models.Model):
    day_schedule = models.ForeignKey(DaySchedule, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    unique_code = models.CharField(
        max_length=20,
        unique=True,
        default=get_random_string,
    )
    expired = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket {self.unique_code} for user {self.user_id} on {self.day_schedule.date}"

    def save(self, *args, **kwargs):
        if Ticket.objects.filter(
            day_schedule__doctor=self.day_schedule.doctor,
            user_id=self.user_id,
            expired=False,
            canceled=False,
        ).exists():
            error_message = "An active ticket already exists for this user and doctor."
            raise ValidationError(error_message)

        if not self.unique_code:
            self.unique_code = get_random_string(20)

        super().save(*args, **kwargs)
