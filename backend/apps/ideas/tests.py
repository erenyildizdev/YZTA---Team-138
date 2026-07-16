from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Idea


class IdeaEndpointsTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
            last_name="User",
        )
        self.other_user = self.user_model.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="StrongPass123!",
            first_name="Other",
            last_name="User",
        )
        self.list_url = reverse("ideas:idea-list")
        self.client.force_authenticate(user=self.user)

    def test_create_idea_for_authenticated_user(self):
        payload = {
            "title": "EcoMutfak",
            "description": "A sustainable kitchen waste app.",
            "target_audience": "Environmentally conscious households",
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertTrue(Idea.objects.filter(user=self.user, title=payload["title"]).exists())

    def test_list_only_current_users_ideas(self):
        Idea.objects.create(
            user=self.user,
            title="My Idea",
            description="Owned by current user",
            target_audience="Users",
        )
        Idea.objects.create(
            user=self.other_user,
            title="Other Idea",
            description="Owned by other user",
            target_audience="Users",
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "My Idea")

    def test_retrieve_and_delete_own_idea(self):
        idea = Idea.objects.create(
            user=self.user,
            title="Delete Me",
            description="Should be removable",
            target_audience="Users",
        )

        detail_url = reverse("ideas:idea-detail", kwargs={"pk": idea.pk})

        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Idea.objects.filter(pk=idea.pk).exists())
