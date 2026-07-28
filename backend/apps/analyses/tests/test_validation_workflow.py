from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from apps.analyses.models import (
    MomTestQuestionsAnalysis,
    MoscowScopeAnalysis,
)
from apps.analyses.services.moscow_scope import (
    MoscowGenerationError,
    save_moscow_analysis,
)
from apps.analyses.services.validation_workflow import (
    GENERATION_ERROR,
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    WORKFLOW_STEP_ORDER,
    ValidationWorkflowError,
    run_validation_workflow,
)
from apps.ideas.models import (
    CompetitorAnalysis,
    GeneralEvaluation,
    Idea,
    RiskyAssumptions,
    ValidationRoadmap,
)

EXPECTED_WORKFLOW_STEP_ORDER = (
    "risky_assumptions",
    "mom_test_questions",
    "moscow_scope",
    "validation_roadmap",
    "general_evaluation",
)


class WorkflowTestDataMixin:
    @staticmethod
    def create_idea(user, title):
        return Idea.objects.create(
            user=user,
            title=title,
            description=f"{title} için yeterince uzun bir açıklama.",
            target_audience="Erken aşama girişimciler",
            problem="Doğrulama adımları dağınık ilerliyor.",
            solution="Adımları tek bir akışta çalıştır.",
            sector="SaaS",
        )

    @staticmethod
    def risky_payload(version):
        return {
            "assumptions": [
                {
                    "text": f"{version} riskli varsayım {index}",
                    "level": (
                        "high"
                        if index < 2
                        else "medium"
                    ),
                    "status": "untested",
                }
                for index in range(5)
            ]
        }

    @staticmethod
    def mom_questions(version):
        return [
            {
                "category": f"{version}_category_{index}",
                "question": f"{version} müşteri sorusu {index}?",
            }
            for index in range(10)
        ]

    @staticmethod
    def moscow_payload(version):
        def features(category):
            return [
                {
                    "title": f"{version} {category} {index}",
                    "reason": (
                        f"{category} kategorisindeki {index}. özellik "
                        "MVP kapsamını somutlaştırır."
                    ),
                }
                for index in range(2)
            ]

        return {
            "summary": f"{version} için doğrulanmış MoSCoW özeti.",
            "must_have": features("must"),
            "should_have": features("should"),
            "could_have": features("could"),
            "wont_have": features("wont"),
        }

    @staticmethod
    def roadmap_payload(version, idea):
        phase_keys = (
            "İlk görüşmeler",
            "Test edilecek varsayımlar",
            "MVP öncelikleri",
            "Başarı metrikleri",
            "Sonraki karar noktaları",
        )
        return {
            "roadmap_type": "validation",
            "idea_title": idea.title,
            "phases": [
                {
                    "week": week,
                    "title": f"{version} doğrulama aşaması {week}",
                    **{
                        key: [
                            f"{version} {key} {week}.1",
                            f"{version} {key} {week}.2",
                        ]
                        for key in phase_keys
                    },
                }
                for week in range(1, 4)
            ],
        }

    @staticmethod
    def evaluation_payload(version):
        return {
            "strengths": [
                f"{version} güçlü yön {index}"
                for index in range(3)
            ],
            "uncertainties": [
                f"{version} belirsizlik {index}"
                for index in range(2)
            ],
            "next_action": f"{version} sonraki aksiyon",
        }

    @staticmethod
    def competitor_payload(version):
        return {
            "competitors": [
                {
                    "name": f"{version} rakip",
                    "description": "Benzer problemi çözen mevcut ürün.",
                    "strengths": ["Yerleşik kullanıcı tabanı"],
                    "weaknesses": ["Doğrulama akışı dağınık"],
                }
            ],
            "market_gap": f"{version} pazar boşluğu",
            "differentiation": f"{version} farklılaşma",
        }

    def seed_all_analysis_records(self, idea, version):
        risky = RiskyAssumptions.objects.create(
            idea=idea,
            assumptions_data=self.risky_payload(version),
        )
        mom = MomTestQuestionsAnalysis.objects.create(
            idea=idea,
            questions=self.mom_questions(version),
        )
        moscow = MoscowScopeAnalysis.objects.create(
            idea=idea,
            result=self.moscow_payload(version),
            provider="test-provider",
            model_name="test-model",
        )
        roadmap = ValidationRoadmap.objects.create(
            idea=idea,
            roadmap_data=self.roadmap_payload(version, idea),
        )
        evaluation = GeneralEvaluation.objects.create(
            idea=idea,
            evaluation_data=self.evaluation_payload(version),
        )
        return {
            "risky_assumptions": risky,
            "mom_test_questions": mom,
            "moscow_scope": moscow,
            "validation_roadmap": roadmap,
            "general_evaluation": evaluation,
        }


class ValidationWorkflowEndpointTests(
    WorkflowTestDataMixin,
    APITestCase,
):
    GENERATOR_PATHS = {
        "risky_assumptions": (
            "apps.analyses.services.validation_workflow."
            "generate_risky_assumptions_payload"
        ),
        "mom_test_questions": (
            "apps.analyses.services.validation_workflow."
            "generate_mom_test_questions"
        ),
        "moscow_scope": (
            "apps.analyses.services.validation_workflow."
            "generate_moscow_scope"
        ),
        "validation_roadmap": (
            "apps.analyses.services.validation_workflow."
            "generate_validation_roadmap_payload"
        ),
        "general_evaluation": (
            "apps.analyses.services.validation_workflow."
            "generate_general_evaluation_payload"
        ),
    }

    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="workflow-owner",
            email="workflow-owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = user_model.objects.create_user(
            username="workflow-other",
            email="workflow-other@example.com",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(self.owner, "Workflow Idea")
        self.other_idea = self.create_idea(
            self.other_user,
            "Private Workflow Idea",
        )
        self.url = reverse(
            "analyses:validation-workflow",
            kwargs={"idea_id": self.idea.id},
        )
        self.generation_version = "first"
        self.failure_step = None
        self.failure_exception = None
        self.call_order = []
        self.generator_mocks = {}
        self._start_generator_mocks()

    def _start_generator_mocks(self):
        side_effects = {
            "risky_assumptions": self._generate_risky_assumptions,
            "mom_test_questions": self._generate_mom_test_questions,
            "moscow_scope": self._generate_moscow_scope,
            "validation_roadmap": self._generate_validation_roadmap,
            "general_evaluation": self._generate_general_evaluation,
        }

        for step_name, target in self.GENERATOR_PATHS.items():
            patcher = patch(
                target,
                side_effect=side_effects[step_name],
            )
            self.generator_mocks[step_name] = patcher.start()
            self.addCleanup(patcher.stop)

    def _record_or_fail(self, step_name):
        self.call_order.append(step_name)
        if self.failure_step == step_name:
            raise self.failure_exception

    def _generate_risky_assumptions(self, idea):
        self._record_or_fail("risky_assumptions")
        return self.risky_payload(self.generation_version)

    def _generate_mom_test_questions(self, idea, question_count=10):
        self._record_or_fail("mom_test_questions")
        self.assertEqual(question_count, 10)
        return self.mom_questions(self.generation_version)

    def _generate_moscow_scope(self, idea):
        self._record_or_fail("moscow_scope")
        return save_moscow_analysis(
            idea=idea,
            result=self.moscow_payload(self.generation_version),
            provider="mock-provider",
            model_name="mock-model",
        )

    def _generate_validation_roadmap(self, idea):
        self._record_or_fail("validation_roadmap")
        return self.roadmap_payload(self.generation_version, idea)

    def _generate_general_evaluation(self, idea):
        self._record_or_fail("general_evaluation")
        return self.evaluation_payload(self.generation_version)

    def authenticate(self):
        self.client.force_authenticate(user=self.owner)

    def assert_generators_not_called(self):
        for generator in self.generator_mocks.values():
            generator.assert_not_called()

    def assert_no_owner_analysis_records(self):
        self.assertFalse(
            RiskyAssumptions.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            MomTestQuestionsAnalysis.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            MoscowScopeAnalysis.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            ValidationRoadmap.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            GeneralEvaluation.objects.filter(idea=self.idea).exists()
        )

    def test_unauthenticated_user_cannot_start_workflow(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assert_generators_not_called()
        self.assert_no_owner_analysis_records()

    def test_owner_can_complete_workflow_and_persist_all_results(self):
        self.authenticate()

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "idea_id",
                "status",
                "completed_steps",
                "steps",
            },
        )
        self.assertEqual(response.data["idea_id"], self.idea.id)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(
            response.data["completed_steps"],
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        self.assertEqual(
            [step["name"] for step in response.data["steps"]],
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        self.assertTrue(
            all(
                step["status"] == "completed"
                for step in response.data["steps"]
            )
        )
        for step in response.data["steps"]:
            self.assertEqual(
                set(step),
                {"name", "status", "result"},
            )
        step_results = {
            step["name"]: step["result"]
            for step in response.data["steps"]
        }
        self.assertEqual(
            step_results["risky_assumptions"]["idea"],
            self.idea.id,
        )
        self.assertEqual(
            step_results["risky_assumptions"]["assumptions_data"],
            self.risky_payload("first"),
        )
        self.assertEqual(
            step_results["mom_test_questions"]["idea_id"],
            self.idea.id,
        )
        self.assertEqual(
            step_results["mom_test_questions"]["questions"],
            self.mom_questions("first"),
        )
        self.assertEqual(
            step_results["moscow_scope"]["idea_id"],
            self.idea.id,
        )
        self.assertEqual(
            step_results["moscow_scope"]["summary"],
            self.moscow_payload("first")["summary"],
        )
        self.assertEqual(
            step_results["validation_roadmap"]["idea"],
            self.idea.id,
        )
        self.assertEqual(
            step_results["validation_roadmap"]["roadmap_data"],
            self.roadmap_payload("first", self.idea),
        )
        self.assertEqual(
            step_results["general_evaluation"]["idea"],
            self.idea.id,
        )
        self.assertEqual(
            step_results["general_evaluation"]["evaluation_data"],
            self.evaluation_payload("first"),
        )
        self.assertEqual(
            self.call_order,
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )

        records = {
            "risky_assumptions": RiskyAssumptions.objects.get(
                idea=self.idea
            ),
            "mom_test_questions": MomTestQuestionsAnalysis.objects.get(
                idea=self.idea
            ),
            "moscow_scope": MoscowScopeAnalysis.objects.get(
                idea=self.idea
            ),
            "validation_roadmap": ValidationRoadmap.objects.get(
                idea=self.idea
            ),
            "general_evaluation": GeneralEvaluation.objects.get(
                idea=self.idea
            ),
        }
        for record in records.values():
            self.assertEqual(record.idea_id, self.idea.id)

        self.generator_mocks[
            "risky_assumptions"
        ].assert_called_once_with(self.idea)
        self.generator_mocks[
            "mom_test_questions"
        ].assert_called_once_with(
            self.idea,
            question_count=10,
        )
        self.generator_mocks[
            "moscow_scope"
        ].assert_called_once_with(self.idea)
        self.generator_mocks[
            "validation_roadmap"
        ].assert_called_once_with(self.idea)
        self.generator_mocks[
            "general_evaluation"
        ].assert_called_once_with(self.idea)

    def test_other_users_idea_is_hidden_and_unchanged(self):
        sentinel_records = self.seed_all_analysis_records(
            self.other_idea,
            "private",
        )
        original_values = {
            "risky_assumptions": (
                sentinel_records["risky_assumptions"].assumptions_data
            ),
            "mom_test_questions": (
                sentinel_records["mom_test_questions"].questions
            ),
            "moscow_scope": sentinel_records["moscow_scope"].result,
            "validation_roadmap": (
                sentinel_records["validation_roadmap"].roadmap_data
            ),
            "general_evaluation": (
                sentinel_records["general_evaluation"].evaluation_data
            ),
        }
        self.authenticate()
        url = reverse(
            "analyses:validation-workflow",
            kwargs={"idea_id": self.other_idea.id},
        )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assert_generators_not_called()
        for step_name, record in sentinel_records.items():
            record.refresh_from_db()
            field_name = {
                "risky_assumptions": "assumptions_data",
                "mom_test_questions": "questions",
                "moscow_scope": "result",
                "validation_roadmap": "roadmap_data",
                "general_evaluation": "evaluation_data",
            }[step_name]
            self.assertEqual(
                getattr(record, field_name),
                original_values[step_name],
            )

    def test_missing_idea_returns_404_without_running_services(self):
        self.authenticate()
        url = reverse(
            "analyses:validation-workflow",
            kwargs={"idea_id": 999_999},
        )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assert_generators_not_called()
        self.assert_no_owner_analysis_records()

    def test_provider_failure_stops_later_steps_and_keeps_completed_data(self):
        self.failure_step = "moscow_scope"
        self.failure_exception = MoscowGenerationError(
            "provider-secret-marker"
        )
        self.authenticate()

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            set(response.data),
            {
                "idea_id",
                "status",
                "completed_steps",
                "failed_step",
                "error_code",
                "detail",
                "steps",
            },
        )
        self.assertEqual(response.data["idea_id"], self.idea.id)
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(
            response.data["completed_steps"],
            [
                "risky_assumptions",
                "mom_test_questions",
            ],
        )
        self.assertEqual(response.data["failed_step"], "moscow_scope")
        self.assertEqual(response.data["error_code"], GENERATION_ERROR)
        self.assertEqual(
            response.data["detail"],
            "MoSCoW kapsamı oluşturulamadı. Lütfen tekrar deneyin.",
        )
        self.assertEqual(
            [step["name"] for step in response.data["steps"]],
            [
                "risky_assumptions",
                "mom_test_questions",
            ],
        )
        self.assertEqual(
            response.data["steps"][0]["result"]["assumptions_data"],
            self.risky_payload("first"),
        )
        self.assertEqual(
            response.data["steps"][1]["result"]["questions"],
            self.mom_questions("first"),
        )
        self.assertNotIn(
            "provider-secret-marker",
            str(response.data),
        )
        self.assertEqual(
            self.call_order,
            [
                "risky_assumptions",
                "mom_test_questions",
                "moscow_scope",
            ],
        )
        self.generator_mocks[
            "validation_roadmap"
        ].assert_not_called()
        self.generator_mocks[
            "general_evaluation"
        ].assert_not_called()

        self.assertTrue(
            RiskyAssumptions.objects.filter(idea=self.idea).exists()
        )
        self.assertTrue(
            MomTestQuestionsAnalysis.objects.filter(
                idea=self.idea
            ).exists()
        )
        self.assertFalse(
            MoscowScopeAnalysis.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            ValidationRoadmap.objects.filter(idea=self.idea).exists()
        )
        self.assertFalse(
            GeneralEvaluation.objects.filter(idea=self.idea).exists()
        )

    def test_validation_failure_is_classified_and_sanitized(self):
        validation_cause = serializers.ValidationError(
            "validation-cause-secret-marker"
        )
        validation_error = MoscowGenerationError(
            "validation-wrapper-secret-marker"
        )
        validation_error.__cause__ = validation_cause
        self.failure_step = "moscow_scope"
        self.failure_exception = validation_error
        self.authenticate()

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(
            response.data["completed_steps"],
            [
                "risky_assumptions",
                "mom_test_questions",
            ],
        )
        self.assertEqual(
            response.data["failed_step"],
            "moscow_scope",
        )
        self.assertEqual(response.data["error_code"], VALIDATION_ERROR)
        self.assertNotIn(
            "validation-cause-secret-marker",
            str(response.data),
        )
        self.assertNotIn(
            "validation-wrapper-secret-marker",
            str(response.data),
        )
        self.generator_mocks[
            "validation_roadmap"
        ].assert_not_called()
        self.generator_mocks[
            "general_evaluation"
        ].assert_not_called()

    def test_unexpected_failure_returns_controlled_sanitized_response(self):
        self.failure_step = "risky_assumptions"
        self.failure_exception = RuntimeError(
            "internal-secret-marker"
        )
        self.authenticate()

        with self.assertLogs(
            "apps.analyses.services.validation_workflow",
            level="ERROR",
        ):
            response = self.client.post(self.url, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(response.data["completed_steps"], [])
        self.assertEqual(
            response.data["failed_step"],
            "risky_assumptions",
        )
        self.assertEqual(response.data["error_code"], INTERNAL_ERROR)
        self.assertNotIn(
            "internal-secret-marker",
            str(response.data),
        )
        for step_name in EXPECTED_WORKFLOW_STEP_ORDER[1:]:
            self.generator_mocks[step_name].assert_not_called()
        self.assert_no_owner_analysis_records()

    def test_second_workflow_updates_existing_rows_without_duplicates(self):
        self.authenticate()
        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )
        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )
        first_records = {
            "risky_assumptions": RiskyAssumptions.objects.get(
                idea=self.idea
            ),
            "mom_test_questions": MomTestQuestionsAnalysis.objects.get(
                idea=self.idea
            ),
            "moscow_scope": MoscowScopeAnalysis.objects.get(
                idea=self.idea
            ),
            "validation_roadmap": ValidationRoadmap.objects.get(
                idea=self.idea
            ),
            "general_evaluation": GeneralEvaluation.objects.get(
                idea=self.idea
            ),
        }
        first_ids = {
            name: record.id
            for name, record in first_records.items()
        }

        self.generation_version = "second"
        self.call_order.clear()
        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.call_order,
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        model_map = {
            "risky_assumptions": RiskyAssumptions,
            "mom_test_questions": MomTestQuestionsAnalysis,
            "moscow_scope": MoscowScopeAnalysis,
            "validation_roadmap": ValidationRoadmap,
            "general_evaluation": GeneralEvaluation,
        }
        for step_name, model in model_map.items():
            self.assertEqual(
                model.objects.filter(idea=self.idea).count(),
                1,
            )
            self.assertEqual(
                model.objects.get(idea=self.idea).id,
                first_ids[step_name],
            )

        self.assertEqual(
            RiskyAssumptions.objects.get(
                idea=self.idea
            ).assumptions_data,
            self.risky_payload("second"),
        )
        self.assertEqual(
            MomTestQuestionsAnalysis.objects.get(
                idea=self.idea
            ).questions,
            self.mom_questions("second"),
        )
        self.assertEqual(
            MoscowScopeAnalysis.objects.get(
                idea=self.idea
            ).result,
            self.moscow_payload("second"),
        )
        self.assertEqual(
            ValidationRoadmap.objects.get(
                idea=self.idea
            ).roadmap_data,
            self.roadmap_payload("second", self.idea),
        )
        self.assertEqual(
            GeneralEvaluation.objects.get(
                idea=self.idea
            ).evaluation_data,
            self.evaluation_payload("second"),
        )

    def test_retry_after_partial_failure_reuses_rows_and_completes(self):
        self.failure_step = "moscow_scope"
        self.failure_exception = MoscowGenerationError(
            "temporary provider failure"
        )
        self.authenticate()

        failed_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            failed_response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        first_risky_id = RiskyAssumptions.objects.get(
            idea=self.idea
        ).id
        first_mom_id = MomTestQuestionsAnalysis.objects.get(
            idea=self.idea
        ).id

        self.failure_step = None
        self.failure_exception = None
        self.generation_version = "retry"
        self.call_order.clear()

        success_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            success_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            success_response.data["completed_steps"],
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        self.assertEqual(
            self.call_order,
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        self.assertEqual(
            RiskyAssumptions.objects.get(idea=self.idea).id,
            first_risky_id,
        )
        self.assertEqual(
            MomTestQuestionsAnalysis.objects.get(idea=self.idea).id,
            first_mom_id,
        )
        for model in (
            RiskyAssumptions,
            MomTestQuestionsAnalysis,
            MoscowScopeAnalysis,
            ValidationRoadmap,
            GeneralEvaluation,
        ):
            self.assertEqual(
                model.objects.filter(idea=self.idea).count(),
                1,
            )

    def test_existing_analysis_get_endpoints_return_workflow_results(self):
        self.authenticate()
        workflow_response = self.client.post(
            self.url,
            {},
            format="json",
        )
        self.assertEqual(
            workflow_response.status_code,
            status.HTTP_200_OK,
        )

        endpoint_expectations = (
            (
                reverse(
                    "ideas:idea-risky-assumptions",
                    kwargs={"pk": self.idea.id},
                ),
                {
                    "idea": self.idea.id,
                    "assumptions_data": self.risky_payload("first"),
                },
            ),
            (
                reverse(
                    "analyses:mom-test-question-generate",
                    kwargs={"idea_id": self.idea.id},
                ),
                {
                    "idea_id": self.idea.id,
                    "questions": self.mom_questions("first"),
                },
            ),
            (
                reverse(
                    "analyses:moscow-scope",
                    kwargs={"idea_id": self.idea.id},
                ),
                {
                    "idea_id": self.idea.id,
                    "summary": self.moscow_payload("first")["summary"],
                },
            ),
            (
                reverse(
                    "ideas:idea-roadmap",
                    kwargs={"pk": self.idea.id},
                ),
                {
                    "idea": self.idea.id,
                    "roadmap_data": self.roadmap_payload(
                        "first",
                        self.idea,
                    ),
                },
            ),
            (
                reverse(
                    "ideas:idea-evaluation",
                    kwargs={"pk": self.idea.id},
                ),
                {
                    "idea": self.idea.id,
                    "evaluation_data": self.evaluation_payload("first"),
                },
            ),
        )

        for url, expected_values in endpoint_expectations:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                for field_name, expected_value in (
                    expected_values.items()
                ):
                    self.assertEqual(
                        response.data[field_name],
                        expected_value,
                    )

    def test_existing_generation_post_endpoints_remain_compatible(self):
        self.authenticate()

        with (
            patch(
                "apps.ideas.views.generate_risky_assumptions_payload",
                return_value=self.risky_payload("legacy"),
            ),
            patch(
                "apps.analyses.views.generate_mom_test_questions",
                return_value=self.mom_questions("legacy"),
            ),
            patch(
                "apps.analyses.views.generate_moscow_scope",
                side_effect=lambda idea: save_moscow_analysis(
                    idea=idea,
                    result=self.moscow_payload("legacy"),
                    provider="mock-provider",
                    model_name="mock-model",
                ),
            ),
            patch(
                "apps.ideas.views.generate_validation_roadmap_payload",
                return_value=self.roadmap_payload(
                    "legacy",
                    self.idea,
                ),
            ),
            patch(
                "apps.ideas.views.generate_general_evaluation_payload",
                return_value=self.evaluation_payload("legacy"),
            ),
            patch(
                "apps.ideas.views.generate_competitor_analysis_payload",
                return_value=self.competitor_payload("legacy"),
            ),
        ):
            endpoint_expectations = (
                (
                    reverse(
                        "ideas:idea-generate-risky-assumptions",
                        kwargs={"pk": self.idea.id},
                    ),
                    status.HTTP_201_CREATED,
                    {
                        "idea": self.idea.id,
                        "assumptions_data": self.risky_payload(
                            "legacy"
                        ),
                    },
                ),
                (
                    reverse(
                        "analyses:mom-test-question-generate",
                        kwargs={"idea_id": self.idea.id},
                    ),
                    status.HTTP_200_OK,
                    {
                        "idea_id": self.idea.id,
                        "framework": "the_mom_test",
                        "question_count": 10,
                        "questions": self.mom_questions("legacy"),
                    },
                ),
                (
                    reverse(
                        "analyses:moscow-scope",
                        kwargs={"idea_id": self.idea.id},
                    ),
                    status.HTTP_201_CREATED,
                    {
                        "idea_id": self.idea.id,
                        "summary": self.moscow_payload(
                            "legacy"
                        )["summary"],
                    },
                ),
                (
                    reverse(
                        "ideas:idea-generate-roadmap",
                        kwargs={"pk": self.idea.id},
                    ),
                    status.HTTP_201_CREATED,
                    {
                        "idea": self.idea.id,
                        "roadmap_data": self.roadmap_payload(
                            "legacy",
                            self.idea,
                        ),
                    },
                ),
                (
                    reverse(
                        "ideas:idea-generate-evaluation",
                        kwargs={"pk": self.idea.id},
                    ),
                    status.HTTP_201_CREATED,
                    {
                        "idea": self.idea.id,
                        "evaluation_data": self.evaluation_payload(
                            "legacy"
                        ),
                    },
                ),
                (
                    reverse(
                        "ideas:idea-generate-competitor-analysis",
                        kwargs={"pk": self.idea.id},
                    ),
                    status.HTTP_201_CREATED,
                    {
                        "idea": self.idea.id,
                        "analysis_data": self.competitor_payload(
                            "legacy"
                        ),
                    },
                ),
            )

            for url, expected_status, expected_values in (
                endpoint_expectations
            ):
                with self.subTest(url=url):
                    response = self.client.post(
                        url,
                        {},
                        format="json",
                    )
                    self.assertEqual(
                        response.status_code,
                        expected_status,
                    )
                    for field_name, expected_value in (
                        expected_values.items()
                    ):
                        self.assertEqual(
                            response.data[field_name],
                            expected_value,
                        )

        self.assertEqual(
            RiskyAssumptions.objects.get(
                idea=self.idea
            ).assumptions_data,
            self.risky_payload("legacy"),
        )
        self.assertEqual(
            MomTestQuestionsAnalysis.objects.get(
                idea=self.idea
            ).questions,
            self.mom_questions("legacy"),
        )
        self.assertEqual(
            MoscowScopeAnalysis.objects.get(
                idea=self.idea
            ).result,
            self.moscow_payload("legacy"),
        )
        self.assertEqual(
            ValidationRoadmap.objects.get(
                idea=self.idea
            ).roadmap_data,
            self.roadmap_payload("legacy", self.idea),
        )
        self.assertEqual(
            GeneralEvaluation.objects.get(
                idea=self.idea
            ).evaluation_data,
            self.evaluation_payload("legacy"),
        )
        self.assertEqual(
            CompetitorAnalysis.objects.get(
                idea=self.idea
            ).analysis_data,
            self.competitor_payload("legacy"),
        )

    def test_early_failure_does_not_delete_existing_later_results(self):
        existing = self.seed_all_analysis_records(
            self.idea,
            "existing",
        )
        original_ids = {
            name: record.id
            for name, record in existing.items()
        }
        original_mom_questions = list(
            existing["mom_test_questions"].questions
        )
        original_moscow_result = dict(
            existing["moscow_scope"].result
        )
        original_roadmap = dict(
            existing["validation_roadmap"].roadmap_data
        )
        original_evaluation = dict(
            existing["general_evaluation"].evaluation_data
        )
        self.failure_step = "mom_test_questions"
        self.failure_exception = ValueError(
            "invalid generated questions"
        )
        self.generation_version = "updated"
        self.authenticate()

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.data["completed_steps"],
            ["risky_assumptions"],
        )
        self.assertEqual(
            RiskyAssumptions.objects.get(idea=self.idea).id,
            original_ids["risky_assumptions"],
        )
        self.assertEqual(
            RiskyAssumptions.objects.get(
                idea=self.idea
            ).assumptions_data,
            self.risky_payload("updated"),
        )

        unchanged_expectations = (
            (
                MomTestQuestionsAnalysis,
                "mom_test_questions",
                "questions",
                original_mom_questions,
            ),
            (
                MoscowScopeAnalysis,
                "moscow_scope",
                "result",
                original_moscow_result,
            ),
            (
                ValidationRoadmap,
                "validation_roadmap",
                "roadmap_data",
                original_roadmap,
            ),
            (
                GeneralEvaluation,
                "general_evaluation",
                "evaluation_data",
                original_evaluation,
            ),
        )
        for model, step_name, field_name, expected_value in (
            unchanged_expectations
        ):
            record = model.objects.get(idea=self.idea)
            self.assertEqual(record.id, original_ids[step_name])
            self.assertEqual(
                getattr(record, field_name),
                expected_value,
            )


class ValidationWorkflowServiceTests(
    WorkflowTestDataMixin,
    TestCase,
):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="workflow-service-owner",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(user, "Service Workflow Idea")

    @patch(
        "apps.analyses.services.validation_workflow._run_step"
    )
    def test_service_runs_each_step_in_exact_order(self, run_step):
        self.assertEqual(
            WORKFLOW_STEP_ORDER,
            EXPECTED_WORKFLOW_STEP_ORDER,
        )
        run_step.side_effect = (
            lambda step_name, _idea: {"step": step_name}
        )

        result = run_validation_workflow(self.idea)

        self.assertEqual(
            run_step.call_args_list,
            [
                call(step_name, self.idea)
                for step_name in EXPECTED_WORKFLOW_STEP_ORDER
            ],
        )
        self.assertEqual(
            [step.name for step in result.steps],
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        self.assertEqual(
            result.as_response()["completed_steps"],
            list(EXPECTED_WORKFLOW_STEP_ORDER),
        )

    @patch(
        "apps.analyses.services.validation_workflow._run_step"
    )
    def test_service_stops_on_generation_error(self, run_step):
        def side_effect(step_name, _idea):
            if step_name == "moscow_scope":
                raise MoscowGenerationError("provider-private-detail")
            return {"step": step_name}

        run_step.side_effect = side_effect

        with self.assertRaises(ValidationWorkflowError) as context:
            run_validation_workflow(self.idea)

        error = context.exception
        self.assertEqual(error.error_code, GENERATION_ERROR)
        self.assertEqual(error.failed_step, "moscow_scope")
        self.assertEqual(
            [
                step.name
                for step in error.completed_steps
            ],
            [
                "risky_assumptions",
                "mom_test_questions",
            ],
        )
        self.assertEqual(
            run_step.call_args_list,
            [
                call("risky_assumptions", self.idea),
                call("mom_test_questions", self.idea),
                call("moscow_scope", self.idea),
            ],
        )
        self.assertNotIn(
            "provider-private-detail",
            str(error.as_response()),
        )

    @patch(
        "apps.analyses.services.validation_workflow._run_step",
        side_effect=RuntimeError("internal-private-detail"),
    )
    def test_service_classifies_unexpected_error_without_leaking_it(
        self,
        run_step,
    ):
        with self.assertLogs(
            "apps.analyses.services.validation_workflow",
            level="ERROR",
        ):
            with self.assertRaises(ValidationWorkflowError) as context:
                run_validation_workflow(self.idea)

        error = context.exception
        self.assertEqual(error.error_code, INTERNAL_ERROR)
        self.assertEqual(
            error.failed_step,
            "risky_assumptions",
        )
        self.assertEqual(error.completed_steps, ())
        self.assertNotIn(
            "internal-private-detail",
            str(error.as_response()),
        )
        run_step.assert_called_once_with(
            "risky_assumptions",
            self.idea,
        )
