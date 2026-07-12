from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analyses.services import generate_mom_test_questions
from apps.ideas.models import Idea


class MomTestQuestionEndpointTests(APITestCase):
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
        self.idea = Idea.objects.create(
            user=self.user,
            title="EcoMutfak",
            description="A sustainable kitchen waste app.",
            target_audience="Environmentally conscious households",
        )
        self.other_idea = Idea.objects.create(
            user=self.other_user,
            title="Other Idea",
            description="Owned by another user.",
            target_audience="Other users",
        )
        self.url = reverse("analyses:mom-test-question-generate", kwargs={"idea_id": self.idea.pk})

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def post_to_endpoint(self, data=None, idea=None):
        url = reverse(
            "analyses:mom-test-question-generate",
            kwargs={"idea_id": (idea or self.idea).pk},
        )
        return self.client.post(url, data or {}, format="json")

    def test_unauthenticated_request_returns_401(self):
        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_generate_mom_test_questions(self):
        self.authenticate()

        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_idea_returns_404(self):
        self.authenticate()
        url = reverse("analyses:mom-test-question-generate", kwargs={"idea_id": 999999})

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_idea_returns_404(self):
        self.authenticate()

        response = self.post_to_endpoint(idea=self.other_idea)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_request_body_returns_default_ten_questions(self):
        self.authenticate()

        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_count"], 10)
        self.assertEqual(len(response.data["questions"]), 10)

    def test_question_count_eight_returns_eight_questions(self):
        self.authenticate()

        response = self.post_to_endpoint({"question_count": 8})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_count"], 8)
        self.assertEqual(len(response.data["questions"]), 8)

    def test_question_count_nine_returns_nine_questions(self):
        self.authenticate()

        response = self.post_to_endpoint({"question_count": 9})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_count"], 9)
        self.assertEqual(len(response.data["questions"]), 9)

    def test_question_count_ten_returns_ten_questions(self):
        self.authenticate()

        response = self.post_to_endpoint({"question_count": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_count"], 10)
        self.assertEqual(len(response.data["questions"]), 10)

    def test_question_count_below_minimum_returns_400(self):
        self.authenticate()

        response = self.post_to_endpoint({"question_count": 7})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_question_count_above_maximum_returns_400(self):
        self.authenticate()

        response = self.post_to_endpoint({"question_count": 11})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_contains_expected_fields(self):
        self.authenticate()

        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("idea_id", response.data)
        self.assertIn("framework", response.data)
        self.assertIn("question_count", response.data)
        self.assertIn("questions", response.data)

    def test_response_framework_is_the_mom_test(self):
        self.authenticate()

        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["framework"], "the_mom_test")

    def test_each_question_contains_category_and_question(self):
        self.authenticate()

        response = self.post_to_endpoint()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for question in response.data["questions"]:
            self.assertEqual(set(question.keys()), {"category", "question"})

    def test_question_categories_are_unique(self):
        self.authenticate()

        response = self.post_to_endpoint()

        categories = [question["category"] for question in response.data["questions"]]
        self.assertEqual(len(categories), len(set(categories)))

    def test_question_texts_are_unique(self):
        self.authenticate()

        response = self.post_to_endpoint()

        questions = [question["question"] for question in response.data["questions"]]
        self.assertEqual(len(questions), len(set(questions)))

    def test_service_returns_deterministic_questions_for_same_input(self):
        first_result = generate_mom_test_questions(self.idea, question_count=10)
        second_result = generate_mom_test_questions(self.idea, question_count=10)

        self.assertEqual(first_result, second_result)
