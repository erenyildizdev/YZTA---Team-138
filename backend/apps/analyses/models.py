import uuid

from django.core.exceptions import ValidationError
from django.db import models
from pgvector.django import VectorField

from .workflow_contract import (
    WORKFLOW_ERROR_CODES,
    WORKFLOW_STAGE_STATUSES,
    WORKFLOW_STEP_ORDER,
)


def default_validation_workflow_stages():
    return {
        step_name: "pending"
        for step_name in WORKFLOW_STEP_ORDER
    }


class ValidationWorkflowRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="validation_workflow_runs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    current_stage = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    failed_stage = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    stages = models.JSONField(
        default=default_validation_workflow_stages,
    )
    error_code = models.CharField(
        max_length=50,
        choices=tuple(
            (error_code, error_code)
            for error_code in WORKFLOW_ERROR_CODES
        ),
        null=True,
        blank=True,
    )
    terminal_response = models.JSONField(
        null=True,
        blank=True,
    )
    terminal_status_code = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["idea"],
                condition=models.Q(
                    status__in=(
                        "pending",
                        "running",
                    )
                ),
                name="unique_active_validation_workflow_run",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=(
                        "pending",
                        "running",
                        "completed",
                        "failed",
                    )
                ),
                name="valid_validation_workflow_run_status",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(current_stage__isnull=True)
                    | models.Q(current_stage__in=WORKFLOW_STEP_ORDER)
                ),
                name="valid_validation_workflow_current_stage",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(failed_stage__isnull=True)
                    | models.Q(failed_stage__in=WORKFLOW_STEP_ORDER)
                ),
                name="valid_validation_workflow_failed_stage",
            ),
        ]

    def clean(self):
        super().clean()
        expected_stages = set(WORKFLOW_STEP_ORDER)
        if (
            not isinstance(self.stages, dict)
            or set(self.stages) != expected_stages
            or any(
                stage_status not in WORKFLOW_STAGE_STATUSES
                for stage_status in self.stages.values()
            )
        ):
            raise ValidationError(
                {
                    "stages": (
                        "Stages must contain every workflow stage with a "
                        "supported status."
                    )
                }
            )

    def __str__(self):
        return f"Validation workflow {self.id} for {self.idea}"


class MoscowScopeAnalysis(models.Model):
    idea = models.OneToOneField(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="moscow_scope_analysis",
    )
    result = models.JSONField()
    prompt_version = models.CharField(max_length=50, default="moscow-v1")
    provider = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MoSCoW scope for {self.idea}"


class MomTestQuestionsAnalysis(models.Model):
    idea = models.OneToOneField(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="mom_test_questions_analysis",
    )
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mom Test questions for {self.idea}"


class InterviewNote(models.Model):
    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="interview_notes",
    )
    interviewee_name = models.CharField(max_length=255, blank=True)
    interviewee_profile = models.CharField(max_length=500, blank=True)
    notes = models.TextField()
    interviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        subject = self.interviewee_name or f"Note {self.pk or 'unsaved'}"
        return f"{subject} - {self.idea.title}"

class InterviewEvidenceAnalysis(models.Model):
    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="interview_evidence_analyses",
    )
    interview_notes = models.ManyToManyField(
        InterviewNote,
        related_name="evidence_analyses",
    )
    result = models.JSONField()
    prompt_version = models.CharField(
        max_length=50,
        default="interview-evidence-v1",
    )
    provider = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Interview evidence analysis for {self.idea}"


class KnowledgeSource(models.Model):
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, default="text")
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class KnowledgeChunk(models.Model):
    source = models.ForeignKey(
        KnowledgeSource,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    content = models.TextField()
    chunk_index = models.PositiveIntegerField()
    embedding = VectorField(dimensions=768)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["source", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "chunk_index"],
                name="unique_source_chunk_index",
            )
        ]

    def __str__(self):
        return f"{self.source.title} - Chunk {self.chunk_index}"
