from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analyses.models import MoscowScopeAnalysis
from apps.analyses.services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
    parse_and_validate_moscow_result,
)
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


def valid_moscow_result():
    categories = {
        "must_have": ("Fikir kaydı", "Temel girdiler olmadan fikir analizi yapılamaz."),
        "should_have": ("Analiz geçmişi", "Önceki sonuçlara dönmek karşılaştırma yapmayı kolaylaştırır."),
        "could_have": ("PDF dışa aktarım", "Sonuçların paydaşlarla paylaşılmasını kolaylaştırır."),
        "wont_have": ("Ödeme altyapısı", "İlk MVP değerini sınamak için ödeme sistemi gerekli değildir."),
    }
    result = {
        "summary": "MVP temel fikir doğrulama akışına odaklanmalıdır.",
        **{key: [{"title": title, "reason": reason}] for key, (title, reason) in categories.items()},
    }
    result["must_have"] += [
        {"title": "Hedef kitle girişi", "reason": "Analizin doğru kullanıcı bağlamında yapılmasını sağlar."},
        {"title": "MoSCoW analizi", "reason": "Temel özellikleri MVP önceliklerine göre ayırır."},
    ]
    result["should_have"].append(
        {"title": "Yeniden oluşturma", "reason": "Fikir geliştikçe kapsamın tekrar değerlendirilmesini sağlar."}
    )
    result["could_have"].append(
        {"title": "Ekip paylaşımı", "reason": "Ekip üyelerinin aynı kapsam üzerinde çalışmasını kolaylaştırır."}
    )
    return result


class StubMoscowClient:
    provider = "test-provider"
    model_name = "test-model"

    def __init__(self, response):
        self.response = response
        self.calls = 0

    def complete(self, prompt):
        self.calls += 1
        return self.response


class MoscowScopeServiceTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="service", password="pass")
        self.idea = Idea.objects.create(
            user=user, title="Scope tool", description="Prioritizes an MVP.", target_audience="Founders"
        )

    def test_valid_result_is_saved_with_metadata(self):
        analysis = generate_moscow_scope(self.idea, client=StubMoscowClient(valid_moscow_result()))
        self.assertEqual(analysis.provider, "test-provider")
        self.assertEqual(analysis.result["summary"], valid_moscow_result()["summary"])

    def test_missing_category_is_rejected(self):
        result = valid_moscow_result()
        del result["could_have"]
        with self.assertRaises(MoscowGenerationError):
            parse_and_validate_moscow_result(result)

    def test_empty_title_or_reason_is_rejected(self):
        for field in ("title", "reason"):
            result = valid_moscow_result()
            result["must_have"][0][field] = ""
            with self.subTest(field=field), self.assertRaises(MoscowGenerationError):
                parse_and_validate_moscow_result(result)

    def test_duplicate_titles_are_case_insensitively_rejected(self):
        result = valid_moscow_result()
        result["wont_have"][0]["title"] = "  FİKİR KAYDI  "
        with self.assertRaises(MoscowGenerationError):
            parse_and_validate_moscow_result(result)

    def test_feature_count_outside_limits_is_rejected(self):
        result = valid_moscow_result()
        result["must_have"] = result["must_have"][:1]
        with self.assertRaises(MoscowGenerationError):
            parse_and_validate_moscow_result(result)

    def test_malformed_json_retries_once_then_raises(self):
        client = StubMoscowClient("not json")
        with self.assertRaises(MoscowGenerationError):
            generate_moscow_scope(self.idea, client=client)
        self.assertEqual(client.calls, 2)


class MoscowScopeEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner2", password="pass")
        self.other_user = get_user_model().objects.create_user(username="other2", password="pass")
        self.idea = Idea.objects.create(
            user=self.user, title="Scope tool", description="Prioritizes an MVP.", target_audience="Founders"
        )
        self.other_idea = Idea.objects.create(
            user=self.other_user, title="Private", description="Private idea.", target_audience="Teams"
        )
        self.url = reverse("analyses:moscow-scope", kwargs={"idea_id": self.idea.pk})

    def authenticate(self):
        self.client.force_authenticate(self.user)

    @patch("apps.analyses.views.generate_moscow_scope")
    def test_owner_can_create_and_response_has_all_categories(self, generate):
        self.authenticate()
        generate.side_effect = lambda idea: MoscowScopeAnalysis.objects.create(idea=idea, result=valid_moscow_result())
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MoscowScopeAnalysis.objects.count(), 1)
        for category in ("must_have", "should_have", "could_have", "wont_have"):
            self.assertIn(category, response.data)

    def test_get_returns_saved_result(self):
        self.authenticate()
        MoscowScopeAnalysis.objects.create(idea=self.idea, result=valid_moscow_result())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["idea_id"], self.idea.pk)

    def test_get_without_analysis_returns_404(self):
        self.authenticate()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.analyses.views.generate_moscow_scope")
    def test_second_post_updates_without_duplicate(self, generate):
        self.authenticate()
        existing = MoscowScopeAnalysis.objects.create(idea=self.idea, result=valid_moscow_result())
        generate.side_effect = lambda idea: MoscowScopeAnalysis.objects.update_or_create(
            idea=idea, defaults={"result": valid_moscow_result()}
        )[0]
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MoscowScopeAnalysis.objects.filter(idea=self.idea).count(), 1)
        self.assertEqual(response.data["id"], existing.id)

    def test_unauthenticated_request_returns_401(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_users_idea_is_hidden(self):
        self.authenticate()
        url = reverse("analyses:moscow-scope", kwargs={"idea_id": self.other_idea.pk})
        self.assertEqual(self.client.post(url, {}).status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_idea_returns_404(self):
        self.authenticate()
        url = reverse("analyses:moscow-scope", kwargs={"idea_id": 999999})
        self.assertEqual(self.client.post(url, {}).status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.analyses.views.generate_moscow_scope", side_effect=MoscowGenerationError())
    def test_generation_failure_returns_controlled_502(self, _generate):
        self.authenticate()
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data, {"detail": "The MoSCoW scope could not be generated."})
