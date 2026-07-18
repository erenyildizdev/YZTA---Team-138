from django.db import models
from pgvector.django import VectorField

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
