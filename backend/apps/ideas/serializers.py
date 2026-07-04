from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ["id", "title", "description", "target_audience", "created_at"]
        read_only_fields = ["id", "created_at", "user"]
