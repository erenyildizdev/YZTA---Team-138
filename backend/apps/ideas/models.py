from django.conf import settings
from django.db import models


class Idea(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas")
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_audience = models.CharField(max_length=255)
    problem = models.TextField()
    solution = models.TextField()
    sector = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    rag_sources = models.JSONField(
    default=list,
    blank=True,
    )

    def __str__(self):
        return self.title

class ValidationRoadmap(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name="validation_roadmap")
    roadmap_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Validation roadmap for {self.idea.title}"

class RiskyAssumptions(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name="risky_assumptions")
    assumptions_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Risky assumptions for {self.idea.title}"

class GeneralEvaluation(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name="general_evaluation")
    evaluation_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"General evaluation for {self.idea.title}"

class CompetitorAnalysis(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name="competitor_analysis")
    analysis_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Competitor analysis for {self.idea.title}"