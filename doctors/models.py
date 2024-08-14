from django.contrib.postgres.fields import ArrayField
from django.db import models


class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def default_active_days():
    return [1, 2, 3, 4, 5]  # Monday to Friday


class DefaultSchedule(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    active_days = ArrayField(
        base_field=models.IntegerField(),
        help_text="List of active days as integers: 1=Monday, 2=Tuesday, etc.",
        default=default_active_days,
    )
    default_patient_count = models.PositiveIntegerField()

    def __str__(self):
        return f"Default Schedule for {self.doctor}"


class DaySchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    max_patients = models.PositiveIntegerField()
    patients = models.JSONField(default=list, help_text="List of patient IDs")

    def __str__(self):
        return f"Schedule for {self.doctor} on {self.date}"

    def save(self, *args, **kwargs):
        if len(self.patients) > self.max_patients:
            error_message = "The number of patients exceeds the maximum allowed for this day."
            raise ValueError(error_message)
        super().save(*args, **kwargs)
