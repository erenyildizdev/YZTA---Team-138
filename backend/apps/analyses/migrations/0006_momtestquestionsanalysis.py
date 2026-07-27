from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("analyses", "0005_interviewevidenceanalysis"),
        ("ideas", "0005_generalevaluation"),
    ]

    operations = [
        migrations.CreateModel(
            name="MomTestQuestionsAnalysis",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("questions", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "idea",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mom_test_questions_analysis",
                        to="ideas.idea",
                    ),
                ),
            ],
        ),
    ]
