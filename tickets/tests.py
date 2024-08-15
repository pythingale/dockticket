from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from doctors.models import DaySchedule
from doctors.models import Doctor


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def doctor():
    return Doctor.objects.create(
        first_name="John",
        last_name="Doe",
        speciality="Cardiology",
        address="123 Street",
        phone_number="123456789",
    )


@pytest.fixture()
def day_schedule(doctor):
    today = now().date()
    return DaySchedule.objects.create(doctor=doctor, date=today, max_patients=10)


@pytest.mark.django_db()
def test_create_ticket_success(api_client, doctor, day_schedule):
    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Ticket successfully created"
    assert "ticket_code" in response.data
    assert "schedule_date" in response.data
    assert "doctor_id" in response.data


@pytest.mark.django_db()
def test_ticket_creation_with_no_user(api_client, doctor):
    url = reverse("ticket-list")
    data = {"doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "user_id" in response.data


@pytest.mark.django_db()
def test_ticket_creation_with_no_doctor(api_client):
    url = reverse("ticket-list")
    data = {"user_id": 1}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "doctor_id" in response.data


@pytest.mark.django_db()
def test_ticket_creation_with_empty_payload(api_client):
    url = reverse("ticket-list")
    data = {}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "user_id" in response.data
    assert "doctor_id" in response.data


@pytest.mark.django_db()
def test_ticket_creation_with_non_existent_doctor(api_client):
    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": 9999}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@pytest.mark.django_db()
def test_ticket_creation_fails_when_capacity_is_full(api_client, doctor, day_schedule):
    # Fill the schedule
    day_schedule.patients = [i for i in range(10)]
    day_schedule.save()

    url = reverse("ticket-list")
    data = {"user_id": 11, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "No available slots for this doctor this week."


@pytest.mark.django_db()
def test_ticket_assigned_to_next_available_day(api_client, doctor):
    today = now().date()
    day_schedule_today = DaySchedule.objects.create(
        doctor=doctor,
        date=today,
        max_patients=10,
        patients=[i for i in range(10)],
    )
    tomorrow = today + timedelta(days=1)
    day_schedule_tomorrow = DaySchedule.objects.create(doctor=doctor, date=tomorrow, max_patients=10)

    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["schedule_date"] == str(tomorrow)


@pytest.mark.django_db()
def test_create_ticket_for_next_week(api_client, doctor):
    today = now().date()
    next_week = today + timedelta(days=7)
    day_schedule_next_week = DaySchedule.objects.create(doctor=doctor, date=next_week, max_patients=10)

    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["schedule_date"] == str(next_week)


@pytest.mark.django_db()
def test_ticket_creation_when_no_schedule_for_week(api_client, doctor):
    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@pytest.mark.django_db()
def test_ticket_creation_for_last_day_of_week(api_client, doctor):
    today = now().date()
    end_of_week = today + timedelta(days=(7 - today.weekday()) - 1)
    day_schedule_end_of_week = DaySchedule.objects.create(doctor=doctor, date=end_of_week, max_patients=10)

    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["schedule_date"] == str(end_of_week)


@pytest.mark.django_db()
def test_ticket_creation_for_middle_day_of_week(api_client, doctor):
    today = now().date()
    middle_day_of_week = today - timedelta(days=today.weekday() - 3)
    day_schedule_middle_day = DaySchedule.objects.create(doctor=doctor, date=middle_day_of_week, max_patients=10)

    url = reverse("ticket-list")
    data = {"user_id": 1, "doctor_id": doctor.id}

    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["schedule_date"] == str(middle_day_of_week)
