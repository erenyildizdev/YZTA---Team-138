import uuid

import apps.analyses.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analyses", "0006_momtestquestionsanalysis"),
        ("ideas", "0008_investorpitch"),
    ]

    operations = [
        migrations.CreateModel(
            name="ValidationWorkflowRun",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "current_stage",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "failed_stage",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "stages",
                    models.JSONField(
                        default=(
                            apps.analyses.models
                            .default_validation_workflow_stages
                        ),
                    ),
                ),
                (
                    "error_code",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("generation_error", "generation_error"),
                            ("validation_error", "validation_error"),
                            ("internal_error", "internal_error"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "terminal_response",
                    models.JSONField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "terminal_status_code",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "finished_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "idea",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="validation_workflow_runs",
                        to="ideas.idea",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(
                            ("status__in", ("pending", "running"))
                        ),
                        fields=("idea",),
                        name="unique_active_validation_workflow_run",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            (
                                "status__in",
                                (
                                    "pending",
                                    "running",
                                    "completed",
                                    "failed",
                                ),
                            )
                        ),
                        name="valid_validation_workflow_run_status",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("current_stage__isnull", True),
                            (
                                "current_stage__in",
                                (
                                    "risky_assumptions",
                                    "mom_test_questions",
                                    "moscow_scope",
                                    "validation_roadmap",
                                    "general_evaluation",
                                ),
                            ),
                            _connector="OR",
                        ),
                        name="valid_validation_workflow_current_stage",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("failed_stage__isnull", True),
                            (
                                "failed_stage__in",
                                (
                                    "risky_assumptions",
                                    "mom_test_questions",
                                    "moscow_scope",
                                    "validation_roadmap",
                                    "general_evaluation",
                                ),
                            ),
                            _connector="OR",
                        ),
                        name="valid_validation_workflow_failed_stage",
                    ),
                ],
            },
        ),
    ]
