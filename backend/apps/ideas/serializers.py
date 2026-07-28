from rest_framework import serializers

from .models import CompetitorAnalysis, GeneralEvaluation, Idea, RiskyAssumptions, ValidationRoadmap


class IdeaSerializer(serializers.ModelSerializer):
    analysis_status = serializers.SerializerMethodField()
    completed_analysis_count = serializers.SerializerMethodField()
    total_analysis_count = serializers.IntegerField(default=5, read_only=True)
    sources = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "description",
            "target_audience",
            "problem",
            "solution",
            "sector",
            "created_at",
            "analysis_status",
            "completed_analysis_count",
            "total_analysis_count",
            "sources",
        ]
        read_only_fields = ["id", "created_at", "user"]

    required_analysis_relations = (
        "risky_assumptions",
        "mom_test_questions_analysis",
        "moscow_scope_analysis",
        "validation_roadmap",
        "general_evaluation",
    )

    def get_completed_analysis_count(self, obj):
        return sum(
            hasattr(obj, relation)
            for relation in self.required_analysis_relations
        )

    def get_analysis_status(self, obj):
        completed_count = self.get_completed_analysis_count(obj)

        if completed_count == 0:
            return "draft"

        if completed_count == len(self.required_analysis_relations):
            return "completed"

        return "in_progress"

    def get_sources(self, obj):
        return obj.rag_sources or []


class ValidationRoadmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRoadmap
        fields = ["id", "idea", "roadmap_data", "created_at"]
        read_only_fields = fields


class RiskyAssumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskyAssumptions
        fields = ["id", "idea", "assumptions_data", "created_at"]
        read_only_fields = fields


class GeneralEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralEvaluation
        fields = ["id", "idea", "evaluation_data", "created_at"]
        read_only_fields = fields


class CompetitorAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorAnalysis
        fields = ["id", "idea", "analysis_data", "created_at"]
        read_only_fields = fields
