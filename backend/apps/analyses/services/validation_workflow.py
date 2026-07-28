import json
import logging
from dataclasses import dataclass
from typing import Any

from rest_framework import serializers as drf_serializers

from apps.analyses.models import MomTestQuestionsAnalysis
from apps.analyses.serializers import (
    MomTestQuestionResponseSerializer,
    MoscowScopeAnalysisSerializer,
)
from apps.ideas.models import (
    GeneralEvaluation,
    RiskyAssumptions,
    ValidationRoadmap,
)
from apps.ideas.serializers import (
    GeneralEvaluationSerializer,
    RiskyAssumptionsSerializer,
    ValidationRoadmapSerializer,
)
from apps.ideas.services import (
    GeneralEvaluationGenerationError,
    RiskyAssumptionsGenerationError,
    RoadmapGenerationError,
    generate_general_evaluation_payload,
    generate_risky_assumptions_payload,
    generate_validation_roadmap_payload,
)

from .llm_client import LLMClientError
from .mom_test_questions import generate_mom_test_questions
from .moscow_scope import MoscowGenerationError, generate_moscow_scope
from .validation_workflow_contract import (
    GENERATION_ERROR,
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    WORKFLOW_STEP_ORDER,
)

logger = logging.getLogger(__name__)

_GENERATION_ERRORS = (
    GeneralEvaluationGenerationError,
    LLMClientError,
    MoscowGenerationError,
    RiskyAssumptionsGenerationError,
    RoadmapGenerationError,
)

_VALIDATION_CAUSES = (
    drf_serializers.ValidationError,
    json.JSONDecodeError,
    ValueError,
)

_STEP_FAILURE_DETAILS = {
    "risky_assumptions": (
        "Riskli varsayımlar oluşturulamadı. Lütfen tekrar deneyin."
    ),
    "mom_test_questions": (
        "Mom Test soruları oluşturulamadı. Lütfen tekrar deneyin."
    ),
    "moscow_scope": (
        "MoSCoW kapsamı oluşturulamadı. Lütfen tekrar deneyin."
    ),
    "validation_roadmap": (
        "Doğrulama yol haritası oluşturulamadı. Lütfen tekrar deneyin."
    ),
    "general_evaluation": (
        "Genel değerlendirme oluşturulamadı. Lütfen tekrar deneyin."
    ),
}


@dataclass(frozen=True)
class WorkflowStepResult:
    name: str
    result: dict[str, Any]

    def as_response(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": "completed",
            "result": self.result,
        }


@dataclass(frozen=True)
class ValidationWorkflowResult:
    idea_id: int
    steps: tuple[WorkflowStepResult, ...]

    def as_response(self) -> dict[str, Any]:
        return {
            "idea_id": self.idea_id,
            "status": "completed",
            "completed_steps": [step.name for step in self.steps],
            "steps": [step.as_response() for step in self.steps],
        }


class ValidationWorkflowError(Exception):
    def __init__(
        self,
        *,
        idea_id: int,
        failed_step: str,
        completed_steps: list[WorkflowStepResult],
        error_code: str,
        detail: str,
    ):
        super().__init__(detail)
        self.idea_id = idea_id
        self.failed_step = failed_step
        self.completed_steps = tuple(completed_steps)
        self.error_code = error_code
        self.detail = detail

    def as_response(self) -> dict[str, Any]:
        return {
            "idea_id": self.idea_id,
            "status": "failed",
            "completed_steps": [
                step.name
                for step in self.completed_steps
            ],
            "failed_step": self.failed_step,
            "error_code": self.error_code,
            "detail": self.detail,
            "steps": [
                step.as_response()
                for step in self.completed_steps
            ],
        }


def _run_risky_assumptions(idea) -> dict[str, Any]:
    payload = generate_risky_assumptions_payload(idea)
    analysis, _ = RiskyAssumptions.objects.update_or_create(
        idea=idea,
        defaults={"assumptions_data": payload},
    )
    return dict(RiskyAssumptionsSerializer(analysis).data)


def _run_mom_test_questions(idea) -> dict[str, Any]:
    question_count = 10
    questions = generate_mom_test_questions(
        idea,
        question_count=question_count,
    )
    response_serializer = MomTestQuestionResponseSerializer(
        data={
            "idea_id": idea.id,
            "framework": "the_mom_test",
            "question_count": question_count,
            "questions": questions,
        }
    )
    response_serializer.is_valid(raise_exception=True)

    MomTestQuestionsAnalysis.objects.update_or_create(
        idea=idea,
        defaults={"questions": questions},
    )
    return dict(response_serializer.data)


def _run_moscow_scope(idea) -> dict[str, Any]:
    analysis = generate_moscow_scope(idea)
    return dict(MoscowScopeAnalysisSerializer(analysis).data)


def _run_validation_roadmap(idea) -> dict[str, Any]:
    payload = generate_validation_roadmap_payload(idea)
    roadmap, _ = ValidationRoadmap.objects.update_or_create(
        idea=idea,
        defaults={"roadmap_data": payload},
    )
    return dict(ValidationRoadmapSerializer(roadmap).data)


def _run_general_evaluation(idea) -> dict[str, Any]:
    payload = generate_general_evaluation_payload(idea)
    evaluation, _ = GeneralEvaluation.objects.update_or_create(
        idea=idea,
        defaults={"evaluation_data": payload},
    )
    return dict(GeneralEvaluationSerializer(evaluation).data)


def _run_step(step_name, idea) -> dict[str, Any]:
    runners = {
        "risky_assumptions": _run_risky_assumptions,
        "mom_test_questions": _run_mom_test_questions,
        "moscow_scope": _run_moscow_scope,
        "validation_roadmap": _run_validation_roadmap,
        "general_evaluation": _run_general_evaluation,
    }
    return runners[step_name](idea)


def _has_validation_cause(exc: BaseException) -> bool:
    current: BaseException | None = exc
    visited = set()

    while current is not None and id(current) not in visited:
        if isinstance(current, _VALIDATION_CAUSES):
            return True
        visited.add(id(current))
        current = current.__cause__ or current.__context__

    return False


def run_validation_workflow(idea) -> ValidationWorkflowResult:
    completed_steps: list[WorkflowStepResult] = []

    for step_name in WORKFLOW_STEP_ORDER:
        try:
            result = _run_step(step_name, idea)
        except _GENERATION_ERRORS as exc:
            error_code = (
                VALIDATION_ERROR
                if _has_validation_cause(exc)
                else GENERATION_ERROR
            )
            raise ValidationWorkflowError(
                idea_id=idea.id,
                failed_step=step_name,
                completed_steps=completed_steps,
                error_code=error_code,
                detail=_STEP_FAILURE_DETAILS[step_name],
            ) from exc
        except (drf_serializers.ValidationError, ValueError) as exc:
            raise ValidationWorkflowError(
                idea_id=idea.id,
                failed_step=step_name,
                completed_steps=completed_steps,
                error_code=VALIDATION_ERROR,
                detail=_STEP_FAILURE_DETAILS[step_name],
            ) from exc
        except Exception as exc:
            logger.exception(
                "Validation workflow step '%s' failed unexpectedly.",
                step_name,
            )
            raise ValidationWorkflowError(
                idea_id=idea.id,
                failed_step=step_name,
                completed_steps=completed_steps,
                error_code=INTERNAL_ERROR,
                detail=(
                    "Doğrulama akışı tamamlanamadı. "
                    "Lütfen daha sonra tekrar deneyin."
                ),
            ) from exc

        completed_steps.append(
            WorkflowStepResult(
                name=step_name,
                result=result,
            )
        )

    return ValidationWorkflowResult(
        idea_id=idea.id,
        steps=tuple(completed_steps),
    )
