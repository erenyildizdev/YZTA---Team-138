from unittest.mock import patch

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

        # Testler varsayılan olarak ana kullanıcıyla çalışır.
        self.client.force_authenticate(user=self.user)

    def create_idea(self, user=None, title="Test Idea"):
        return Idea.objects.create(
            user=user or self.user,
            title=title,
            description="Test description",
            target_audience="Students",
            problem="Test problem",
            solution="Test solution",
            sector="Technology",
        )

    def test_create_idea_for_authenticated_user(self):
        payload = {
            "title": "EcoMutfak",
            "description": "A sustainable kitchen waste app.",
            "target_audience": "Environmentally conscious households",

            "problem": "Households struggle to track kitchen waste.",
            "solution": "Help households measure and reduce their waste.",
            "sector": "Sustainability",
            "problem": "Households have difficulty reducing kitchen waste.",
            "solution": "An application that helps users track and reduce waste.",
            "sector": "Technology",
        }

        response = self.client.post(
            self.list_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["title"],
            payload["title"],
        )
        self.assertTrue(
            Idea.objects.filter(
                user=self.user,
                title=payload["title"],
            ).exists()
        )

    def test_list_only_current_users_ideas(self):
        self.create_idea(
            user=self.user,
            title="My Idea",
        )

        self.create_idea(
            user=self.other_user,
            title="Other Idea",
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "My Idea",
        )

    def test_retrieve_and_delete_own_idea(self):
        idea = self.create_idea(
            title="Delete Me",
        )

        detail_url = reverse(
            "ideas:idea-detail",
            kwargs={"pk": idea.pk},
        )

        retrieve_response = self.client.get(detail_url)

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_200_OK,
        )

        delete_response = self.client.delete(detail_url)

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Idea.objects.filter(pk=idea.pk).exists()
        )

    @patch("apps.ideas.views.analyze_idea")
    def test_owner_can_analyze_idea(self, mock_analyze_idea):
        idea = self.create_idea()

        mock_analyze_idea.return_value = {
            "idea_summary": "Test summary",
            "rag_used": True,
            "sources": [],
        }

        response = self.client.post(
            f"/api/ideas/{idea.id}/analyze/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["idea_summary"],
            "Test summary",
        )
        self.assertTrue(response.data["rag_used"])

        mock_analyze_idea.assert_called_once()

        sent_idea_text = (
            mock_analyze_idea.call_args.kwargs["idea_text"]
        )

        self.assertIn(idea.title, sent_idea_text)
        self.assertIn(idea.description, sent_idea_text)
        self.assertIn(idea.problem, sent_idea_text)
        self.assertIn(idea.solution, sent_idea_text)

    @patch("apps.ideas.views.analyze_idea")
    def test_user_cannot_analyze_another_users_idea(
        self,
        mock_analyze_idea,
    ):
        idea = self.create_idea(
            user=self.other_user,
            title="Other User Idea",
        )

        response = self.client.post(
            f"/api/ideas/{idea.id}/analyze/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        mock_analyze_idea.assert_not_called()

    @patch("apps.ideas.views.analyze_idea")
    def test_unauthenticated_user_cannot_analyze_idea(
        self,
        mock_analyze_idea,
    ):
        idea = self.create_idea()

        # setUp içinde yapılan authentication'ı kaldırır.
        self.client.force_authenticate(user=None)

        response = self.client.post(
            f"/api/ideas/{idea.id}/analyze/",
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
        mock_analyze_idea.assert_not_called()