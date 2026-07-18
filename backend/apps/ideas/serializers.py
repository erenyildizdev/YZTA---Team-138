from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):
    problem = serializers.CharField(required=False, allow_blank=True)
    solution = serializers.CharField(required=False, allow_blank=True)
    sector_category = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "description",
            "target_audience",
            "problem",
            "solution",
            "sector_category",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]
