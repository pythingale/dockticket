from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from .models import DaySchedule
from .models import DefaultSchedule
from .models import Doctor


@shared_task
def create_day_schedules():
    today = now().date()
    next_week = today + timedelta(weeks=1)

    doctors = Doctor.objects.all()

    for doctor in doctors:
        try:
            default_schedule = DefaultSchedule.objects.get(doctor=doctor)
            current_day = today

            while current_day <= next_week:
                day_of_week = current_day.isoweekday()  # Monday is 1 and Sunday is 7
                if day_of_week in default_schedule.active_days:
                    if not DaySchedule.objects.filter(
                        doctor=doctor,
                        date=current_day,
                    ).exists():
                        DaySchedule.objects.create(
                            doctor=doctor,
                            date=current_day,
                            max_patients=default_schedule.default_patient_count,
                            patients=[],
                        )
                current_day += timedelta(days=1)

        except DefaultSchedule.DoesNotExist:
            continue
