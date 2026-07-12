from rest_framework import serializers


class MomTestQuestionRequestSerializer(serializers.Serializer):
    question_count = serializers.IntegerField(required=False, default=10, min_value=8, max_value=10)


class MomTestQuestionSerializer(serializers.Serializer):
    category = serializers.CharField()
    question = serializers.CharField()


class MomTestQuestionResponseSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    framework = serializers.CharField()
    question_count = serializers.IntegerField()
    questions = MomTestQuestionSerializer(many=True)
