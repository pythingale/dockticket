import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("docticket")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure the Celery Beat schedule
app.conf.beat_schedule = {
    "create-day-schedules-every-day": {
        "task": "doctors.tasks.create_day_schedules",
        "schedule": crontab(hour=0, minute=0),
    },
    "expire-tickets-every-day": {
        "task": "tickets.tasks.expire_old_tickets",
        "schedule": crontab(hour=0, minute=0),
    },
}
