from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_valid_data(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(reverse("user:create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_user_invalid_data(self):
        data = {
            "username": "testuser",
            "password": "test",
        }

        response = self.client.post(reverse("user:create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="testuser").exists())


class LoginTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_login_valid_data(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(reverse("user:token_obtain_pair"), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_data(self):
        data = {
            "username": "invaliduser",
            "password": "invalidpassword",
        }

        response = self.client.post(reverse("user:token_obtain_pair"), data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
