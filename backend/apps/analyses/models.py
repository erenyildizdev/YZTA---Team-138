from django.db import models


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
