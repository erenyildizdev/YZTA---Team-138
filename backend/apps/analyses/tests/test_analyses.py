from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analyses.models import (
    InterviewEvidenceAnalysis,
    InterviewNote,
    MoscowScopeAnalysis,
)
from apps.analyses.services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
    parse_and_validate_moscow_result,
)
from apps.ideas.models import Idea

from apps.analyses.services.llm_client import LLMClientError
from apps.analyses.services.interview_evidence import (
    InterviewNotesNotFoundError,
    analyze_interview_evidence,
)

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
        self.generate_patcher = patch(
            "apps.analyses.views.generate_mom_test_questions",
            side_effect=self._generated_questions,
        )
        self.mock_generate = self.generate_patcher.start()
        self.addCleanup(self.generate_patcher.stop)

    @staticmethod
    def _generated_questions(_idea, question_count=10):
        return [
            {
                "category": f"category_{index}",
                "question": f"Fikre özel soru {index}?",
            }
            for index in range(question_count)
        ]

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

    @patch(
        "apps.analyses.services.mom_test_questions.call_mom_test_llm"
    )
    def test_service_returns_generated_questions(
        self,
        mock_call_mom_test_llm,
    ):
        mock_questions = [
            {
                "category": f"category_{i}",
                "question": f"Fikre özel soru {i}?",
            }
            for i in range(10)
        ]

        mock_call_mom_test_llm.return_value = {
            "questions": mock_questions,
        }

        result = generate_mom_test_questions(
            self.idea,
            question_count=10,
        )

        self.assertEqual(result, mock_questions)
        mock_call_mom_test_llm.assert_called_once()

    @patch(
        "apps.analyses.services.mom_test_questions.call_mom_test_llm",
        return_value={"questions": [{"category": "only", "question": "Tek soru?"}]},
    )
    def test_invalid_provider_response_uses_deterministic_fallback(self, mock_call):
        result = generate_mom_test_questions(self.idea, question_count=8)

        self.assertEqual(len(result), 8)
        self.assertEqual(result[0]["category"], "problem_context")
        mock_call.assert_called_once()

    @patch(
        "apps.analyses.services.mom_test_questions.call_mom_test_llm",
        side_effect=LLMClientError("provider unavailable"),
    )
    def test_provider_error_uses_deterministic_fallback(self, mock_call):
        result = generate_mom_test_questions(self.idea, question_count=10)

        self.assertEqual(len(result), 10)
        self.assertEqual(result[-1]["category"], "commitment_signal")
        mock_call.assert_called_once()


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


class InterviewNoteEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="interview-owner",
            password="pass",
        )
        self.other_user = get_user_model().objects.create_user(
            username="interview-other",
            password="pass",
        )
        self.idea = self._create_idea(
            self.user,
            "Interview tracker",
        )
        self.second_idea = self._create_idea(
            self.user,
            "Second owned idea",
        )
        self.other_idea = self._create_idea(
            self.other_user,
            "Other user's idea",
        )
        self.note = InterviewNote.objects.create(
            idea=self.idea,
            interviewee_name="Ada",
            interviewee_profile="Product manager",
            notes="Ada described her current workflow.",
        )
        self.second_idea_note = InterviewNote.objects.create(
            idea=self.second_idea,
            notes="This note belongs to another owned idea.",
        )
        self.other_note = InterviewNote.objects.create(
            idea=self.other_idea,
            notes="This note belongs to another user.",
        )
        self.list_url = reverse(
            "analyses:interview-note-list-create",
            kwargs={"idea_id": self.idea.pk},
        )
        self.detail_url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.idea.pk,
                "note_id": self.note.pk,
            },
        )

    def _create_idea(self, user, title):
        return Idea.objects.create(
            user=user,
            title=title,
            description="An idea used by the interview note tests.",
            target_audience="Founders",
            problem="Interview notes are scattered.",
            solution="Keep interview notes together.",
            sector="SaaS",
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_user_cannot_list_notes(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_note(self):
        response = self.client.post(
            self.list_url,
            {"notes": "Private interview notes."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_retrieve_note(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_create_note_for_idea_from_url(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {
                "interviewee_name": "  Grace Hopper  ",
                "interviewee_profile": "  Technical founder  ",
                "notes": "  Uses manual reports every Friday.  ",
                "interviewed_at": "2026-07-20T12:30:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data),
            {
                "id",
                "idea_id",
                "interviewee_name",
                "interviewee_profile",
                "notes",
                "interviewed_at",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(response.data["idea_id"], self.idea.pk)
        self.assertEqual(response.data["interviewee_name"], "Grace Hopper")
        self.assertEqual(
            response.data["interviewee_profile"],
            "Technical founder",
        )
        self.assertEqual(
            response.data["notes"],
            "Uses manual reports every Friday.",
        )

        note = InterviewNote.objects.get(pk=response.data["id"])
        self.assertEqual(note.idea, self.idea)
        self.assertEqual(note.interviewee_name, "Grace Hopper")
        self.assertIsNotNone(note.interviewed_at)

    def test_create_requires_notes(self):
        self.authenticate()

        response = self.client.post(self.list_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notes", response.data)

    def test_create_rejects_empty_notes(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {"notes": ""},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_whitespace_only_notes(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {"notes": " \t\n "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_invalid_interviewed_at(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {
                "notes": "Valid notes.",
                "interviewed_at": "not-a-datetime",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("interviewed_at", response.data)

    def test_create_accepts_null_interviewed_at(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {
                "notes": "Valid notes.",
                "interviewed_at": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["interviewed_at"])

    def test_create_rejects_idea_fields_from_request_body(self):
        self.authenticate()

        for field in ("idea", "idea_id"):
            with self.subTest(field=field):
                before_count = InterviewNote.objects.count()
                response = self.client.post(
                    self.list_url,
                    {
                        "notes": "Attempted relationship change.",
                        field: self.second_idea.pk,
                    },
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)
                self.assertEqual(
                    InterviewNote.objects.count(),
                    before_count,
                )

    def test_create_enforces_string_length_limits(self):
        self.authenticate()
        invalid_values = (
            ("interviewee_name", "n" * 256),
            ("interviewee_profile", "p" * 501),
            ("notes", "x" * 10_001),
        )

        for field, value in invalid_values:
            with self.subTest(field=field):
                payload = {"notes": "Valid notes.", field: value}
                response = self.client.post(
                    self.list_url,
                    payload,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)

    def test_owner_can_list_only_notes_for_requested_idea(self):
        self.authenticate()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.data],
            [self.note.pk],
        )

    def test_other_users_idea_is_hidden_from_list(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-list-create",
            kwargs={"idea_id": self.other_idea.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_idea_is_hidden_from_create(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-list-create",
            kwargs={"idea_id": self.other_idea.pk},
        )
        before_count = InterviewNote.objects.count()

        response = self.client.post(
            url,
            {"notes": "Attempted foreign note."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(InterviewNote.objects.count(), before_count)

    def test_notes_are_listed_newest_first(self):
        self.authenticate()
        first_note = self.note
        second_note = InterviewNote.objects.create(
            idea=self.idea,
            notes="A newer interview.",
        )
        now = timezone.now()
        InterviewNote.objects.filter(pk=first_note.pk).update(
            created_at=now - timedelta(days=1),
        )
        InterviewNote.objects.filter(pk=second_note.pk).update(
            created_at=now,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.data],
            [second_note.pk, first_note.pk],
        )

    def test_owner_can_retrieve_note(self):
        self.authenticate()

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.note.pk)
        self.assertEqual(response.data["idea_id"], self.idea.pk)

    def test_other_users_note_is_hidden(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.other_idea.pk,
                "note_id": self.other_note.pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_note_must_belong_to_idea_in_url(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.idea.pk,
                "note_id": self.second_idea_note.pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch_note(self):
        self.authenticate()

        response = self.client.patch(
            self.detail_url,
            {
                "interviewee_profile": "  Engineering manager  ",
                "notes": "  Updated workflow details.  ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["interviewee_profile"],
            "Engineering manager",
        )
        self.assertEqual(
            response.data["notes"],
            "Updated workflow details.",
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.notes, "Updated workflow details.")

    def test_owner_can_put_note(self):
        self.authenticate()

        response = self.client.put(
            self.detail_url,
            {
                "interviewee_name": "Lin",
                "interviewee_profile": "Founder",
                "notes": "A complete replacement of the interview note.",
                "interviewed_at": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.interviewee_name, "Lin")
        self.assertEqual(
            self.note.notes,
            "A complete replacement of the interview note.",
        )

    def test_put_requires_notes(self):
        self.authenticate()

        response = self.client.put(
            self.detail_url,
            {"interviewee_name": "Lin"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notes", response.data)

    def test_other_users_note_cannot_be_updated(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.other_idea.pk,
                "note_id": self.other_note.pk,
            },
        )

        response = self.client.patch(
            url,
            {"notes": "Attempted update."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_note.refresh_from_db()
        self.assertEqual(
            self.other_note.notes,
            "This note belongs to another user.",
        )

    def test_cross_idea_note_cannot_be_updated_or_deleted(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.idea.pk,
                "note_id": self.second_idea_note.pk,
            },
        )

        patch_response = self.client.patch(
            url,
            {"notes": "Attempted cross-idea update."},
            format="json",
        )
        delete_response = self.client.delete(url)

        self.assertEqual(
            patch_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.second_idea_note.refresh_from_db()
        self.assertEqual(
            self.second_idea_note.notes,
            "This note belongs to another owned idea.",
        )

    def test_update_rejects_relationship_changes(self):
        self.authenticate()

        for field in ("idea", "idea_id"):
            with self.subTest(field=field):
                response = self.client.patch(
                    self.detail_url,
                    {field: self.second_idea.pk},
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)
                self.note.refresh_from_db()
                self.assertEqual(self.note.idea, self.idea)

    def test_update_rejects_empty_notes(self):
        self.authenticate()

        response = self.client.patch(
            self.detail_url,
            {"notes": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.notes,
            "Ada described her current workflow.",
        )

    def test_owner_can_delete_note(self):
        self.authenticate()
        note_id = self.note.pk

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            InterviewNote.objects.filter(pk=note_id).exists()
        )

    def test_other_users_note_cannot_be_deleted(self):
        self.authenticate()
        url = reverse(
            "analyses:interview-note-detail",
            kwargs={
                "idea_id": self.other_idea.pk,
                "note_id": self.other_note.pk,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            InterviewNote.objects.filter(pk=self.other_note.pk).exists()
        )


class IdeaAnalysisEndpointTests(APITestCase):

    def setUp(self):
        self.url = "/api/analyses/analyze/"

    @patch("apps.analyses.views.analyze_idea")
    def test_successful_analysis_returns_200(self, mock_analyze):
        mock_analyze.return_value = {
            "idea_summary": "Test fikri özeti",
            "target_customer": "Üniversite öğrencileri",
            "problem_statement": "Öğrenciler uygun fiyatlı sağlıklı beslenmekte zorlanıyor.",
            "value_proposition": "Bütçeye uygun sağlıklı yemek planları sunar.",
            "risky_assumptions": [
                "Öğrenciler bu hizmeti düzenli kullanır."
            ],
            "mom_test_questions": [
                "Geçtiğimiz hafta yemek planlamasını nasıl yaptın?"
            ],
            "moscow": {
                "must": ["Yemek planı oluşturma"],
                "should": ["Alışveriş listesi"],
                "could": ["Market fiyat karşılaştırması"],
                "wont": ["Yemek teslimatı"],
            },
            "validation_roadmap": [
                "Hedef kullanıcılarla görüş."
            ],
            "evidence_to_collect": [
                "Müşteri görüşme notları"
            ],
            "final_recommendation": "Fikir müşteri görüşmeleriyle doğrulanmalıdır.",
        }

        response = self.client.post(
            self.url,
            {
                "idea_text": "Bu örnek bir iş fikridir."
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["idea_summary"], "Test fikri özeti")

    def test_missing_idea_text_returns_400(self):

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_idea_text_returns_400(self):

        response = self.client.post(
            self.url,
            {
                "idea_text": "abc"
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(
    "apps.analyses.views.analyze_idea",
    side_effect=LLMClientError("AI service is unavailable."),
    )
    def test_ai_service_error_returns_controlled_503(self, _mock_analyze):
        response = self.client.post(
            self.url,
            {
                "idea_text": "Bu yeterince uzun bir iş fikridir."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data,
            {"detail": "AI service is unavailable."},
        )

class InterviewEvidenceAnalysisEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="analysis-owner",
            password="pass",
        )
        self.other_user = get_user_model().objects.create_user(
            username="analysis-other",
            password="pass",
        )

        self.idea = Idea.objects.create(
            user=self.user,
            title="Idea",
            description="Description",
            target_audience="Students",
            problem="Problem",
            solution="Solution",
            sector="Education",
        )

        self.other_idea = Idea.objects.create(
            user=self.other_user,
            title="Other",
            description="Description",
            target_audience="Students",
            problem="Problem",
            solution="Solution",
            sector="Education",
        )

        self.url = reverse(
            "analyses:interview-evidence-analysis",
            kwargs={"idea_id": self.idea.pk},
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_returns_401(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_other_users_idea_returns_404(self):
        self.authenticate()

        url = reverse(
            "analyses:interview-evidence-analysis",
            kwargs={"idea_id": self.other_idea.pk},
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_returns_400_when_no_notes_exist(self):
        self.authenticate()

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("apps.analyses.views.analyze_interview_evidence")
    def test_successful_generation_returns_201(
        self,
        mock_generate,
    ):
        self.authenticate()

        analysis = InterviewEvidenceAnalysis.objects.create(
            idea=self.idea,
            result={
                "supporting_evidence": ["Kanıt"],
                "contradicting_evidence": [],
                "repeated_needs": ["İhtiyaç"],
                "new_risky_assumptions": ["Hipotez"],
                "next_validation_steps": ["Yeni görüşme yap"],
            },
            provider="test",
        )

        mock_generate.return_value = analysis

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["idea_id"],
            self.idea.pk,
        )

    @patch(
        "apps.analyses.views.analyze_interview_evidence",
        side_effect=InterviewNotesNotFoundError("No notes"),
    )
    def test_service_error_returns_400(self, _mock):
        self.authenticate()

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(response.data, {"detail": "No notes"})

    @patch(
        "apps.analyses.views.analyze_interview_evidence",
        side_effect=LLMClientError("AI service is unavailable."),
    )
    def test_llm_error_returns_503(self, _mock):
        self.authenticate()

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data,
            {"detail": "AI service is unavailable."},
        )

    def test_get_without_saved_analysis_returns_404(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_get_returns_latest_saved_analysis(self):
        self.authenticate()

        InterviewEvidenceAnalysis.objects.create(
            idea=self.idea,
            result={
                "supporting_evidence": ["Eski kanıt"],
                "contradicting_evidence": [],
                "repeated_needs": [],
                "new_risky_assumptions": [],
                "next_validation_steps": ["Eski adım"],
            },
        )

        latest = InterviewEvidenceAnalysis.objects.create(
            idea=self.idea,
            result={
                "supporting_evidence": ["Yeni kanıt"],
                "contradicting_evidence": ["Karşı kanıt"],
                "repeated_needs": ["Tekrarlanan ihtiyaç"],
                "new_risky_assumptions": [
                    "Hipotez: Yeni varsayım"
                ],
                "next_validation_steps": ["Yeni görüşme yap"],
            },
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["id"], latest.pk)
        self.assertEqual(
            response.data["supporting_evidence"],
            ["Yeni kanıt"],
        )
        self.assertEqual(
            response.data["next_validation_steps"],
            ["Yeni görüşme yap"],
        )

    def test_get_other_users_idea_returns_404(self):
        self.authenticate()

        InterviewEvidenceAnalysis.objects.create(
            idea=self.other_idea,
            result={
                "supporting_evidence": ["Private evidence"],
                "contradicting_evidence": [],
                "repeated_needs": [],
                "new_risky_assumptions": [],
                "next_validation_steps": ["Private step"],
            },
        )

        url = reverse(
            "analyses:interview-evidence-analysis",
            kwargs={"idea_id": self.other_idea.pk},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @patch("apps.analyses.views.analyze_interview_evidence")
    def test_response_contains_non_empty_next_validation_steps(
        self,
        mock_generate,
    ):
        self.authenticate()

        analysis = InterviewEvidenceAnalysis.objects.create(
            idea=self.idea,
            result={
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "repeated_needs": [],
                "new_risky_assumptions": [],
                "next_validation_steps": [
                    "Üç yeni müşteri görüşmesi yap."
                ],
            },
        )

        mock_generate.return_value = analysis

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(response.data["next_validation_steps"])


class InterviewEvidenceAnalysisServiceTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="evidence-service-owner",
            password="pass",
        )

        self.idea = Idea.objects.create(
            user=self.user,
            title="Primary idea",
            description="Primary description",
            target_audience="Students",
            problem="Primary problem",
            solution="Primary solution",
            sector="Education",
        )

        self.other_idea = Idea.objects.create(
            user=self.user,
            title="Other idea",
            description="Other description",
            target_audience="Teams",
            problem="Other problem",
            solution="Other solution",
            sector="SaaS",
        )

        self.first_note = InterviewNote.objects.create(
            idea=self.idea,
            interviewee_name="Ada",
            notes="Students need a faster workflow.",
        )

        self.second_note = InterviewNote.objects.create(
            idea=self.idea,
            interviewee_name="Lin",
            notes="The current process takes too much time.",
        )

        self.foreign_note = InterviewNote.objects.create(
            idea=self.other_idea,
            interviewee_name="Grace",
            notes="This note must not be included.",
        )

    @patch(
        "apps.analyses.services.interview_evidence."
        "call_interview_analysis_llm"
    )
    def test_only_selected_ideas_notes_are_analyzed(
        self,
        mock_llm,
    ):
        mock_llm.return_value = {
            "supporting_evidence": ["Supporting"],
            "contradicting_evidence": [],
            "repeated_needs": ["Speed"],
            "new_risky_assumptions": [],
            "next_validation_steps": ["Run another interview"],
        }

        analysis = analyze_interview_evidence(self.idea)

        prompt = mock_llm.call_args.kwargs["prompt"]

        self.assertIn(
            "Students need a faster workflow.",
            prompt,
        )
        self.assertIn(
            "The current process takes too much time.",
            prompt,
        )
        self.assertNotIn(
            "This note must not be included.",
            prompt,
        )

        self.assertEqual(
            set(
                analysis.interview_notes.values_list(
                    "id",
                    flat=True,
                )
            ),
            {
                self.first_note.pk,
                self.second_note.pk,
            },
        )
        self.assertFalse(
            analysis.interview_notes.filter(
                pk=self.foreign_note.pk
            ).exists()
        )

    def test_no_notes_raises_error(self):
        empty_idea = Idea.objects.create(
            user=self.user,
            title="Empty idea",
            description="No interviews yet.",
            target_audience="Founders",
            problem="Unknown problem",
            solution="Unknown solution",
            sector="SaaS",
        )

        with self.assertRaises(InterviewNotesNotFoundError):
            analyze_interview_evidence(empty_idea)
