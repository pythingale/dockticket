from django.contrib import admin

from .models import DaySchedule
from .models import DefaultSchedule
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "speciality",
        "phone_number",
        "created_at",
        "updated_at",
    )
    search_fields = ("first_name", "last_name", "speciality", "phone_number")
    ordering = ("last_name", "first_name")


@admin.register(DefaultSchedule)
class DefaultScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "active_days", "default_patient_count")
    search_fields = ("doctor__first_name", "doctor__last_name")
    ordering = ("doctor__last_name",)


@admin.register(DaySchedule)
class DayScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "max_patients")
    search_fields = ("doctor__first_name", "doctor__last_name", "date")
    ordering = ("-date",)
