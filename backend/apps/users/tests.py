from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthEndpointsTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.user_model = get_user_model()

    def test_register_creates_user_and_returns_user_data(self):
        payload = {
            "email": "founder@example.com",
            "password": "StrongPass123!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], payload["email"].lower())
        self.assertTrue(self.user_model.objects.filter(email=payload["email"].lower()).exists())

    def test_login_returns_tokens_for_valid_credentials(self):
        self.user_model.objects.create_user(
            username="tester@example.com",
            email="tester@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
        )

        response = self.client.post(
            self.login_url,
            {"email": "tester@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
