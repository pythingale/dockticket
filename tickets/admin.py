from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "unique_code",
        "user_id",
        "doctor_name",
        "day_schedule_date",
        "expired",
        "canceled",
    )
    list_filter = ("expired", "canceled", "day_schedule__date")
    search_fields = (
        "unique_code",
        "user_id",
        "day_schedule__doctor__first_name",
        "day_schedule__doctor__last_name",
    )
    ordering = ("-day_schedule__date",)

    @admin.display(
        description="Doctor",
    )
    def doctor_name(self, obj):
        return f"{obj.day_schedule.doctor.first_name} {obj.day_schedule.doctor.last_name}"

    @admin.display(
        description="Date of Schedule",
    )
    def day_schedule_date(self, obj):
        return obj.day_schedule.date
