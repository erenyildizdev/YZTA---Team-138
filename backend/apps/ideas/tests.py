from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analyses.models import MomTestQuestionsAnalysis, MoscowScopeAnalysis

from .models import GeneralEvaluation, Idea, RiskyAssumptions, ValidationRoadmap


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

    def test_list_is_newest_first_and_includes_real_analysis_status(self):
        complete_idea = self.create_idea(title="Complete Idea")
        draft_idea = self.create_idea(title="Newest Draft")

        RiskyAssumptions.objects.create(idea=complete_idea)
        MomTestQuestionsAnalysis.objects.create(idea=complete_idea)
        MoscowScopeAnalysis.objects.create(idea=complete_idea, result={})
        ValidationRoadmap.objects.create(idea=complete_idea)
        GeneralEvaluation.objects.create(idea=complete_idea)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["title"] for item in response.data],
            [draft_idea.title, complete_idea.title],
        )
        self.assertEqual(response.data[0]["analysis_status"], "draft")
        self.assertEqual(response.data[0]["completed_analysis_count"], 0)
        self.assertEqual(response.data[1]["analysis_status"], "completed")
        self.assertEqual(response.data[1]["completed_analysis_count"], 5)
        self.assertEqual(response.data[1]["total_analysis_count"], 5)

    def test_partial_analysis_is_in_progress(self):
        idea = self.create_idea(title="Partial Idea")
        RiskyAssumptions.objects.create(idea=idea)

        response = self.client.get(self.list_url)

        self.assertEqual(response.data[0]["analysis_status"], "in_progress")
        self.assertEqual(response.data[0]["completed_analysis_count"], 1)

    def test_list_analysis_summary_does_not_add_queries_per_idea(self):
        for index in range(5):
            self.create_idea(title=f"Idea {index}")

        with self.assertNumQueries(1):
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_unauthenticated_user_cannot_list_ideas(self):
        self.create_idea()
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
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

