import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)

User = get_user_model()


def sample_actor(**params):
    defaults = {"first_name": f"fname", "last_name": "lname"}
    defaults.update(params)
    return Actor.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": f"Genre_{uuid.uuid4().hex[:6]}",
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def sample_play(**params):
    defaults = {
        "title": "Play1",
        "description": "Some text",
        "actors": [sample_actor()],
        "genres": [sample_genre()],
    }
    defaults.update(params)

    play = Play.objects.create(
        title=defaults["title"],
        description=defaults["description"],
    )
    play.actors.set(defaults["actors"])
    play.genres.set(defaults["genres"])
    return play


def sample_theatre_hall(**params):
    defaults = {"name": f"Hall_{uuid.uuid4().hex[:6]}", "rows": 10, "seats_in_row": 20}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def sample_performance(**params):
    defaults = {
        "play": sample_play(),
        "theatre_hall": sample_theatre_hall(),
        "show_time": datetime.datetime.now(),
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


def sample_reservation(**params):
    user = params.pop(
        "user",
        User.objects.create_user(
            username=f"username_{uuid.uuid4().hex[:6]}",
            password=f"password123",
        ),
    )
    defaults = {"created_at": datetime.datetime.now(), "user": user}
    defaults.update(params)
    return Reservation.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "row": 1,
        "seat": 1,
        "performance": sample_performance(),
        "reservation": sample_reservation(),
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


class ReservationUnauthorizedTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_reservations_unauthorized(self):
        response = self.client.get(reverse("theatre:reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_reservation_unauthorized(self):
        data = {
            "performance": sample_performance().id,
            "seats": [{"row": 1, "seat": 1}],
        }

        response = self.client.post(reverse("theatre:reservation-list"), data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Reservation.objects.count(), 0)


class ReservationAuthorizedTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_get_reservations_authorized(self):
        sample_reservation(user=self.user)

        response = self.client.get(reverse("theatre:reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_post_valid_reservation_authorized(self):
        data = {
            "performance": sample_performance().id,
            "seats": [{"row": 1, "seat": 1}],
        }

        response = self.client.post(
            reverse("theatre:reservation-list"), data=data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_post_invalid_reservation_authorized(self):
        data = {
            "performance": sample_performance().id,
            "seats": [{"row": -1, "seat": 228}],
        }

        with self.assertRaises(IntegrityError):
            response = self.client.post(
                reverse("theatre:reservation-list"), data=data, format="json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Reservation.objects.count(), 0)

    def test_post_valid_reservation_creates_tickets(self):
        data = {
            "performance": sample_performance().id,
            "seats": [
                {"row": 1, "seat": 1},
                {"row": 1, "seat": 2},
            ],
        }

        response = self.client.post(
            reverse("theatre:reservation-list"), data=data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.first().tickets.count(), 2)

    def test_delete_reservation_deletes_tickets(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(performance=sample_performance(), reservation=reservation)

        response = self.client.delete(
            reverse("theatre:reservation-detail", args=[reservation.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reservation.objects.filter(user_id=self.user.id).count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_user_sees_only_his_reservations(self):
        sample_reservation(user=self.user)
        sample_reservation()

        response = self.client.get(reverse("theatre:reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.user.id)

    def test_user_sees_only_his_tickets(self):
        user_reservation = sample_reservation(user=self.user)
        other_reservation = sample_reservation()
        sample_ticket(reservation=user_reservation)
        sample_ticket(reservation=other_reservation)

        response = self.client.get(reverse("theatre:ticket-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reservation"], user_reservation.id)
