from dataclasses import dataclass
from uuid import UUID

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.ideas.models import Idea

from ..models import ValidationWorkflowRun
from ..workflow_contract import WORKFLOW_STEP_ORDER


ACTIVE_RUN_STATUSES = (
    ValidationWorkflowRun.Status.PENDING,
    ValidationWorkflowRun.Status.RUNNING,
)


class WorkflowRunAlreadyRunning(Exception):
    def __init__(self, run_id):
        super().__init__(str(run_id))
        self.run_id = run_id


class WorkflowRunIdentityMismatch(Exception):
    """The supplied UUID belongs to a different idea."""


class WorkflowRunStateError(RuntimeError):
    """A progress transition did not match the persisted run state."""


@dataclass(frozen=True)
class WorkflowRunAcquisition:
    run: ValidationWorkflowRun
    should_execute: bool


def acquire_workflow_run(
    idea,
    requested_run_id: UUID | None = None,
) -> WorkflowRunAcquisition:
    """Serialize starts for one idea and either create, attach, or replay."""
    with transaction.atomic():
        Idea.objects.select_for_update().get(pk=idea.pk)

        if requested_run_id is not None:
            existing_run = (
                ValidationWorkflowRun.objects.select_for_update()
                .filter(pk=requested_run_id)
                .first()
            )
            if existing_run is not None:
                if existing_run.idea_id != idea.pk:
                    raise WorkflowRunIdentityMismatch
                if existing_run.status in ACTIVE_RUN_STATUSES:
                    raise WorkflowRunAlreadyRunning(existing_run.pk)
                return WorkflowRunAcquisition(
                    run=existing_run,
                    should_execute=False,
                )

        active_run = (
            ValidationWorkflowRun.objects.select_for_update()
            .filter(
                idea_id=idea.pk,
                status__in=ACTIVE_RUN_STATUSES,
            )
            .first()
        )
        if active_run is not None:
            raise WorkflowRunAlreadyRunning(active_run.pk)

        create_kwargs = {
            "idea_id": idea.pk,
            "status": ValidationWorkflowRun.Status.RUNNING,
        }
        if requested_run_id is not None:
            create_kwargs["id"] = requested_run_id

        try:
            # The inner savepoint keeps the transaction usable if the
            # database constraint catches a writer that did not take the
            # per-idea lock.
            with transaction.atomic():
                run = ValidationWorkflowRun.objects.create(**create_kwargs)
        except IntegrityError:
            active_run = (
                ValidationWorkflowRun.objects.select_for_update()
                .filter(
                    idea_id=idea.pk,
                    status__in=ACTIVE_RUN_STATUSES,
                )
                .first()
            )
            if active_run is not None:
                raise WorkflowRunAlreadyRunning(active_run.pk) from None
            if (
                requested_run_id is not None
                and ValidationWorkflowRun.objects.filter(
                    pk=requested_run_id
                ).exists()
            ):
                raise WorkflowRunIdentityMismatch from None
            raise

    return WorkflowRunAcquisition(run=run, should_execute=True)


class WorkflowRunProgressRecorder:
    """Persist each workflow transition in its own short transaction."""

    def __init__(self, run_id):
        self.run_id = run_id

    def _get_locked_running_run(self):
        try:
            return ValidationWorkflowRun.objects.select_for_update().get(
                pk=self.run_id,
                status=ValidationWorkflowRun.Status.RUNNING,
            )
        except ValidationWorkflowRun.DoesNotExist as exc:
            raise WorkflowRunStateError(
                "The workflow run is no longer running."
            ) from exc

    @staticmethod
    def _require_known_stage(stage_name):
        if stage_name not in WORKFLOW_STEP_ORDER:
            raise WorkflowRunStateError("Unknown workflow stage.")

    def stage_started(self, stage_name):
        self._require_known_stage(stage_name)
        stage_index = WORKFLOW_STEP_ORDER.index(stage_name)

        with transaction.atomic():
            run = self._get_locked_running_run()
            stages = dict(run.stages)
            prior_stages = WORKFLOW_STEP_ORDER[:stage_index]
            if (
                stages.get(stage_name) != "pending"
                or any(
                    stages.get(prior_stage) != "completed"
                    for prior_stage in prior_stages
                )
            ):
                raise WorkflowRunStateError(
                    "The workflow stage cannot be started from its current "
                    "state."
                )

            stages[stage_name] = "running"
            run.stages = stages
            run.current_stage = stage_name
            run.save(
                update_fields=(
                    "stages",
                    "current_stage",
                    "updated_at",
                )
            )

    def stage_completed(self, stage_name):
        self._require_known_stage(stage_name)

        with transaction.atomic():
            run = self._get_locked_running_run()
            stages = dict(run.stages)
            if (
                run.current_stage != stage_name
                or stages.get(stage_name) != "running"
            ):
                raise WorkflowRunStateError(
                    "The workflow stage is not currently running."
                )

            stages[stage_name] = "completed"
            run.stages = stages
            run.current_stage = None
            run.save(
                update_fields=(
                    "stages",
                    "current_stage",
                    "updated_at",
                )
            )

    def stage_failed(self, stage_name, error_code):
        self._require_known_stage(stage_name)
        stage_index = WORKFLOW_STEP_ORDER.index(stage_name)

        with transaction.atomic():
            run = self._get_locked_running_run()
            stages = dict(run.stages)
            if (
                run.current_stage != stage_name
                or stages.get(stage_name) != "running"
            ):
                raise WorkflowRunStateError(
                    "The workflow stage is not currently running."
                )

            stages[stage_name] = "failed"
            for skipped_stage in WORKFLOW_STEP_ORDER[stage_index + 1:]:
                stages[skipped_stage] = "skipped"

            run.status = ValidationWorkflowRun.Status.FAILED
            run.current_stage = None
            run.failed_stage = stage_name
            run.stages = stages
            run.error_code = error_code
            run.finished_at = timezone.now()
            run.save(
                update_fields=(
                    "status",
                    "current_stage",
                    "failed_stage",
                    "stages",
                    "error_code",
                    "finished_at",
                    "updated_at",
                )
            )

    def finalize_success(self, response_data, response_status_code):
        with transaction.atomic():
            run = self._get_locked_running_run()
            if any(
                run.stages.get(stage_name) != "completed"
                for stage_name in WORKFLOW_STEP_ORDER
            ):
                raise WorkflowRunStateError(
                    "A workflow with incomplete stages cannot be completed."
                )

            run.status = ValidationWorkflowRun.Status.COMPLETED
            run.current_stage = None
            run.finished_at = timezone.now()
            run.terminal_response = response_data
            run.terminal_status_code = response_status_code
            run.save(
                update_fields=(
                    "status",
                    "current_stage",
                    "finished_at",
                    "terminal_response",
                    "terminal_status_code",
                    "updated_at",
                )
            )

    def finalize_failure(
        self,
        *,
        failed_stage,
        error_code,
        response_data,
        response_status_code,
    ):
        self._require_known_stage(failed_stage)
        stage_index = WORKFLOW_STEP_ORDER.index(failed_stage)

        with transaction.atomic():
            try:
                run = ValidationWorkflowRun.objects.select_for_update().get(
                    pk=self.run_id,
                    status__in=(
                        ValidationWorkflowRun.Status.RUNNING,
                        ValidationWorkflowRun.Status.FAILED,
                    ),
                )
            except ValidationWorkflowRun.DoesNotExist as exc:
                raise WorkflowRunStateError(
                    "The workflow run cannot be failed."
                ) from exc

            if run.status == ValidationWorkflowRun.Status.RUNNING:
                stages = dict(run.stages)
                stages[failed_stage] = "failed"
                for skipped_stage in WORKFLOW_STEP_ORDER[
                    stage_index + 1:
                ]:
                    stages[skipped_stage] = "skipped"
                run.status = ValidationWorkflowRun.Status.FAILED
                run.current_stage = None
                run.failed_stage = failed_stage
                run.stages = stages
                run.error_code = error_code
                run.finished_at = timezone.now()
            elif (
                run.failed_stage != failed_stage
                or run.error_code != error_code
            ):
                raise WorkflowRunStateError(
                    "The workflow failure does not match its persisted state."
                )

            run.terminal_response = response_data
            run.terminal_status_code = response_status_code
            run.save(
                update_fields=(
                    "status",
                    "current_stage",
                    "failed_stage",
                    "stages",
                    "error_code",
                    "finished_at",
                    "terminal_response",
                    "terminal_status_code",
                    "updated_at",
                )
            )

    def __call__(self, stage_name, stage_status, error_code=None):
        if stage_status == "running":
            self.stage_started(stage_name)
            return
        if stage_status == "completed":
            self.stage_completed(stage_name)
            return
        if stage_status == "failed":
            self.stage_failed(stage_name, error_code)
            return
        raise WorkflowRunStateError("Unknown workflow stage transition.")
