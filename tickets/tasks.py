from celery import shared_task
from django.utils.timezone import now

from .models import Ticket


@shared_task
def expire_old_tickets():
    today = now().date()
    Ticket.objects.filter(day_schedule__date__lt=today, expired=False, canceled=False).update(expired=True)
