from rest_framework import serializers

from .models import GeneralEvaluation, Idea, RiskyAssumptions, ValidationRoadmap


class IdeaSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["id", "created_at", "user"]


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
