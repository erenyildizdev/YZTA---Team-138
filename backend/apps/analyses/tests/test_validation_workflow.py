import threading
import uuid
from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import (
    APIClient,
    APITestCase,
    APITransactionTestCase,
)

from apps.analyses.models import (
    MomTestQuestionsAnalysis,
    MoscowScopeAnalysis,
    ValidationWorkflowRun,
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
from apps.analyses.services.workflow_runs import (
    WorkflowRunProgressRecorder,
    WorkflowRunStateError,
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
                "run_id",
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

    def test_requested_run_uuid_is_persisted_and_owner_scoped(self):
        requested_run_id = uuid.uuid4()
        self.authenticate()

        response = self.client.post(
            self.url,
            {"run_id": str(requested_run_id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["run_id"], str(requested_run_id))

        workflow_run = ValidationWorkflowRun.objects.get(
            pk=requested_run_id
        )
        self.assertEqual(workflow_run.idea_id, self.idea.id)
        self.assertEqual(
            workflow_run.status,
            ValidationWorkflowRun.Status.COMPLETED,
        )
        self.assertIsNone(workflow_run.current_stage)
        self.assertIsNone(workflow_run.failed_stage)
        self.assertIsNone(workflow_run.error_code)
        self.assertIsNotNone(workflow_run.finished_at)
        self.assertEqual(
            workflow_run.stages,
            {
                step_name: "completed"
                for step_name in EXPECTED_WORKFLOW_STEP_ORDER
            },
        )

        progress_url = reverse(
            "analyses:validation-workflow-run",
            kwargs={"run_id": requested_run_id},
        )
        progress_response = self.client.get(progress_url)

        self.assertEqual(
            progress_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            set(progress_response.data),
            {
                "run_id",
                "idea_id",
                "status",
                "current_stage",
                "failed_stage",
                "stages",
                "error_code",
                "created_at",
                "updated_at",
                "finished_at",
            },
        )
        self.assertEqual(
            progress_response.data["run_id"],
            str(requested_run_id),
        )
        self.assertEqual(
            progress_response.data["idea_id"],
            self.idea.id,
        )
        self.assertEqual(
            progress_response.data["status"],
            "completed",
        )

        self.client.force_authenticate(user=self.other_user)
        hidden_response = self.client.get(progress_url)
        self.assertEqual(
            hidden_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_completed_run_id_is_replayed_without_running_generators_again(
        self,
    ):
        requested_run_id = uuid.uuid4()
        self.authenticate()
        first_response = self.client.post(
            self.url,
            {"run_id": str(requested_run_id)},
            format="json",
        )
        first_call_order = list(self.call_order)

        replay_response = self.client.post(
            self.url,
            {"run_id": str(requested_run_id)},
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(replay_response.status_code, status.HTTP_200_OK)
        self.assertEqual(replay_response.data, first_response.data)
        self.assertEqual(self.call_order, first_call_order)
        self.assertEqual(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
            ).count(),
            1,
        )

    def test_terminal_run_without_snapshot_returns_controlled_conflict(self):
        terminal_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.COMPLETED,
        )
        self.authenticate()

        response = self.client.post(
            self.url,
            {"run_id": str(terminal_run.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data,
            {
                "detail": "Bu analiz akışı daha önce tamamlandı.",
                "code": "workflow_run_finished",
                "run_id": str(terminal_run.pk),
            },
        )
        self.assert_generators_not_called()

    def test_active_run_returns_conflict_for_same_or_new_run_id(self):
        active_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.RUNNING,
        )
        self.authenticate()

        same_run_response = self.client.post(
            self.url,
            {"run_id": str(active_run.pk)},
            format="json",
        )
        new_run_response = self.client.post(
            self.url,
            {"run_id": str(uuid.uuid4())},
            format="json",
        )

        for response in (same_run_response, new_run_response):
            self.assertEqual(
                response.status_code,
                status.HTTP_409_CONFLICT,
            )
            self.assertEqual(
                response.data,
                {
                    "detail": (
                        "Bu fikir için bir analiz akışı zaten devam ediyor."
                    ),
                    "code": "workflow_already_running",
                    "run_id": str(active_run.pk),
                },
            )
        self.assert_generators_not_called()
        self.assertEqual(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
            ).count(),
            1,
        )

    def test_run_id_for_a_different_idea_is_rejected(self):
        second_owned_idea = self.create_idea(
            self.owner,
            "Second Owned Idea",
        )
        other_idea_run = ValidationWorkflowRun.objects.create(
            idea=second_owned_idea,
            status=ValidationWorkflowRun.Status.COMPLETED,
        )
        other_user_run = ValidationWorkflowRun.objects.create(
            idea=self.other_idea,
            status=ValidationWorkflowRun.Status.COMPLETED,
        )
        self.authenticate()

        for foreign_run in (other_idea_run, other_user_run):
            with self.subTest(run_id=foreign_run.pk):
                response = self.client.post(
                    self.url,
                    {"run_id": str(foreign_run.pk)},
                    format="json",
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )

        self.assert_generators_not_called()
        self.assertFalse(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
            ).exists()
        )

    def test_invalid_workflow_request_does_not_create_a_run(self):
        self.authenticate()

        invalid_uuid_response = self.client.post(
            self.url,
            {"run_id": "not-a-uuid"},
            format="json",
        )
        unknown_field_response = self.client.post(
            self.url,
            {"unexpected": "value"},
            format="json",
        )

        self.assertEqual(
            invalid_uuid_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            unknown_field_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assert_generators_not_called()
        self.assertFalse(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
            ).exists()
        )

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
                "run_id",
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

        workflow_run = ValidationWorkflowRun.objects.get(
            pk=response.data["run_id"]
        )
        self.assertEqual(
            workflow_run.status,
            ValidationWorkflowRun.Status.FAILED,
        )
        self.assertIsNone(workflow_run.current_stage)
        self.assertEqual(workflow_run.failed_stage, "moscow_scope")
        self.assertEqual(workflow_run.error_code, GENERATION_ERROR)
        self.assertIsNotNone(workflow_run.finished_at)
        self.assertEqual(
            workflow_run.stages,
            {
                "risky_assumptions": "completed",
                "mom_test_questions": "completed",
                "moscow_scope": "failed",
                "validation_roadmap": "skipped",
                "general_evaluation": "skipped",
            },
        )

        progress_url = reverse(
            "analyses:validation-workflow-run",
            kwargs={"run_id": workflow_run.pk},
        )
        progress_response = self.client.get(progress_url)
        self.assertEqual(
            progress_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertNotIn(
            "provider-secret-marker",
            str(progress_response.data),
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

    def test_failed_run_id_is_replayed_without_running_generators_again(
        self,
    ):
        requested_run_id = uuid.uuid4()
        self.failure_step = "moscow_scope"
        self.failure_exception = MoscowGenerationError(
            "temporary-private-detail"
        )
        self.authenticate()
        first_response = self.client.post(
            self.url,
            {"run_id": str(requested_run_id)},
            format="json",
        )
        first_call_order = list(self.call_order)

        replay_response = self.client.post(
            self.url,
            {"run_id": str(requested_run_id)},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertEqual(
            replay_response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertEqual(replay_response.data, first_response.data)
        self.assertEqual(self.call_order, first_call_order)
        self.assertNotIn(
            "temporary-private-detail",
            str(replay_response.data),
        )

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

        workflow_run = ValidationWorkflowRun.objects.get(
            pk=response.data["run_id"]
        )
        self.assertEqual(
            workflow_run.status,
            ValidationWorkflowRun.Status.FAILED,
        )
        self.assertEqual(workflow_run.error_code, INTERNAL_ERROR)
        progress_response = self.client.get(
            reverse(
                "analyses:validation-workflow-run",
                kwargs={"run_id": workflow_run.pk},
            )
        )
        self.assertNotIn(
            "internal-secret-marker",
            str(progress_response.data),
        )

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
        failed_run = ValidationWorkflowRun.objects.get(
            pk=failed_response.data["run_id"]
        )
        failed_run_stages = dict(failed_run.stages)
        failed_run_finished_at = failed_run.finished_at
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
        self.assertNotEqual(
            success_response.data["run_id"],
            failed_response.data["run_id"],
        )
        self.assertEqual(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
            ).count(),
            2,
        )
        failed_run.refresh_from_db()
        self.assertEqual(failed_run.stages, failed_run_stages)
        self.assertEqual(failed_run.finished_at, failed_run_finished_at)
        self.assertEqual(
            failed_run.status,
            ValidationWorkflowRun.Status.FAILED,
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
    def test_service_reports_real_stage_transitions_in_order(
        self,
        run_step,
    ):
        transitions = []
        run_step.side_effect = (
            lambda step_name, _idea: {"step": step_name}
        )

        run_validation_workflow(
            self.idea,
            progress_callback=lambda step, stage_status, error_code: (
                transitions.append(
                    (step, stage_status, error_code)
                )
            ),
        )

        self.assertEqual(
            transitions,
            [
                transition
                for step_name in EXPECTED_WORKFLOW_STEP_ORDER
                for transition in (
                    (step_name, "running", None),
                    (step_name, "completed", None),
                )
            ],
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


class ValidationWorkflowProgressVisibilityTests(
    WorkflowTestDataMixin,
    APITransactionTestCase,
):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="workflow-progress-owner",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(
            self.owner,
            "Visible Workflow Progress",
        )
        self.workflow_url = reverse(
            "analyses:validation-workflow",
            kwargs={"idea_id": self.idea.pk},
        )

    def test_running_stage_is_visible_and_parallel_start_is_rejected(self):
        run_id = uuid.uuid4()
        first_stage_started = threading.Event()
        allow_first_stage_to_finish = threading.Event()
        second_stage_started = threading.Event()
        allow_second_stage_to_finish = threading.Event()
        worker_result = {}

        def run_step(step_name, _idea):
            if step_name == "risky_assumptions":
                first_stage_started.set()
                if not allow_first_stage_to_finish.wait(timeout=10):
                    raise RuntimeError("First test stage release timed out.")
            if step_name == "mom_test_questions":
                second_stage_started.set()
                if not allow_second_stage_to_finish.wait(timeout=10):
                    raise RuntimeError("Second test stage release timed out.")
            return {"step": step_name}

        def start_workflow():
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(user=self.owner)
                worker_result["response"] = client.post(
                    self.workflow_url,
                    {"run_id": str(run_id)},
                    format="json",
                )
            except BaseException as exc:
                worker_result["exception"] = exc
            finally:
                close_old_connections()

        with patch(
            "apps.analyses.services.validation_workflow._run_step",
            side_effect=run_step,
        ) as run_step_mock:
            worker = threading.Thread(target=start_workflow)
            worker.start()
            try:
                self.assertTrue(
                    first_stage_started.wait(timeout=10),
                    "The workflow did not enter its first stage.",
                )

                observer = APIClient()
                observer.force_authenticate(user=self.owner)
                progress_response = observer.get(
                    reverse(
                        "analyses:validation-workflow-run",
                        kwargs={"run_id": run_id},
                    )
                )
                self.assertEqual(
                    progress_response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    progress_response.data["status"],
                    "running",
                )
                self.assertEqual(
                    progress_response.data["current_stage"],
                    "risky_assumptions",
                )
                self.assertEqual(
                    progress_response.data["stages"],
                    {
                        "risky_assumptions": "running",
                        "mom_test_questions": "pending",
                        "moscow_scope": "pending",
                        "validation_roadmap": "pending",
                        "general_evaluation": "pending",
                    },
                )

                allow_first_stage_to_finish.set()
                self.assertTrue(
                    second_stage_started.wait(timeout=10),
                    "The workflow did not enter its second stage.",
                )
                prefix_response = observer.get(
                    reverse(
                        "analyses:validation-workflow-run",
                        kwargs={"run_id": run_id},
                    )
                )
                self.assertEqual(
                    prefix_response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    prefix_response.data["current_stage"],
                    "mom_test_questions",
                )
                self.assertEqual(
                    prefix_response.data["stages"],
                    {
                        "risky_assumptions": "completed",
                        "mom_test_questions": "running",
                        "moscow_scope": "pending",
                        "validation_roadmap": "pending",
                        "general_evaluation": "pending",
                    },
                )

                competing_response = observer.post(
                    self.workflow_url,
                    {"run_id": str(uuid.uuid4())},
                    format="json",
                )
                self.assertEqual(
                    competing_response.status_code,
                    status.HTTP_409_CONFLICT,
                )
                self.assertEqual(
                    competing_response.data["code"],
                    "workflow_already_running",
                )
                self.assertEqual(
                    competing_response.data["run_id"],
                    str(run_id),
                )
                self.assertEqual(run_step_mock.call_count, 2)
            finally:
                allow_first_stage_to_finish.set()
                allow_second_stage_to_finish.set()
                worker.join(timeout=10)

        self.assertFalse(worker.is_alive(), "Workflow thread did not stop.")
        if "exception" in worker_result:
            raise worker_result["exception"]
        self.assertEqual(
            worker_result["response"].status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            run_step_mock.call_count,
            len(EXPECTED_WORKFLOW_STEP_ORDER),
        )
        workflow_run = ValidationWorkflowRun.objects.get(pk=run_id)
        self.assertEqual(
            workflow_run.status,
            ValidationWorkflowRun.Status.COMPLETED,
        )


class ValidationWorkflowRunConstraintTests(
    WorkflowTestDataMixin,
    APITransactionTestCase,
):
    def setUp(self):
        owner = get_user_model().objects.create_user(
            username="workflow-constraint-owner",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(
            owner,
            "Constrained Workflow",
        )

    def test_database_allows_only_one_active_run_per_idea(self):
        first_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.RUNNING,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ValidationWorkflowRun.objects.create(
                    idea=self.idea,
                    status=ValidationWorkflowRun.Status.PENDING,
                )

        first_run.status = ValidationWorkflowRun.Status.COMPLETED
        first_run.save(update_fields=("status", "updated_at"))
        second_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.RUNNING,
        )

        self.assertNotEqual(first_run.pk, second_run.pk)
        self.assertEqual(
            ValidationWorkflowRun.objects.filter(
                idea=self.idea,
                status__in=("pending", "running"),
            ).count(),
            1,
        )

    def test_stale_recorder_cannot_mutate_a_newer_active_run(self):
        old_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.FAILED,
            failed_stage="risky_assumptions",
            stages={
                "risky_assumptions": "failed",
                "mom_test_questions": "skipped",
                "moscow_scope": "skipped",
                "validation_roadmap": "skipped",
                "general_evaluation": "skipped",
            },
            error_code=GENERATION_ERROR,
        )
        new_run = ValidationWorkflowRun.objects.create(
            idea=self.idea,
            status=ValidationWorkflowRun.Status.RUNNING,
        )
        original_new_stages = dict(new_run.stages)

        with self.assertRaises(WorkflowRunStateError):
            WorkflowRunProgressRecorder(old_run.pk).stage_started(
                "risky_assumptions"
            )

        old_run.refresh_from_db()
        new_run.refresh_from_db()
        self.assertEqual(
            old_run.status,
            ValidationWorkflowRun.Status.FAILED,
        )
        self.assertEqual(new_run.stages, original_new_stages)
        self.assertIsNone(new_run.current_stage)
