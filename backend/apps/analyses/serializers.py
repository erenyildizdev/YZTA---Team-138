import unicodedata

from rest_framework import serializers

from .models import MoscowScopeAnalysis


class IdeaAnalysisRequestSerializer(serializers.Serializer):
    idea_text = serializers.CharField(min_length=10)


class StrictFieldsSerializer(serializers.Serializer):
    """Reject unknown structured-output fields instead of silently dropping them."""

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected an object.")

        unknown = set(data) - set(self.fields)

        if unknown:
            raise serializers.ValidationError(
                {field: "Unexpected field." for field in sorted(unknown)}
            )

        return super().to_internal_value(data)


class MoscowFeatureSerializer(StrictFieldsSerializer):
    title = serializers.CharField(
        min_length=3,
        max_length=100,
        trim_whitespace=True,
    )
    reason = serializers.CharField(
        min_length=10,
        max_length=500,
        trim_whitespace=True,
    )


class MoscowScopeResultSerializer(StrictFieldsSerializer):
    CATEGORY_FIELDS = (
        "must_have",
        "should_have",
        "could_have",
        "wont_have",
    )

    summary = serializers.CharField(
        min_length=10,
        max_length=1000,
        trim_whitespace=True,
    )
    must_have = MoscowFeatureSerializer(many=True, allow_empty=False)
    should_have = MoscowFeatureSerializer(many=True, allow_empty=False)
    could_have = MoscowFeatureSerializer(many=True, allow_empty=False)
    wont_have = MoscowFeatureSerializer(many=True, allow_empty=False)

    @staticmethod
    def _canonical_title(value):
        folded = unicodedata.normalize("NFKD", value.casefold())
        without_marks = "".join(
            character
            for character in folded
            if not unicodedata.combining(character)
        )
        return without_marks.replace("ı", "i")

    def validate(self, attrs):
        features = [
            item
            for category in self.CATEGORY_FIELDS
            for item in attrs[category]
        ]

        if not 8 <= len(features) <= 12:
            raise serializers.ValidationError(
                "The result must contain 8 to 12 features."
            )

        titles = [
            self._canonical_title(item["title"])
            for item in features
        ]

        if len(titles) != len(set(titles)):
            raise serializers.ValidationError(
                "Feature titles must be unique across categories."
            )

        return attrs


class MoscowScopeAnalysisSerializer(serializers.ModelSerializer):
    idea_id = serializers.IntegerField(read_only=True)
    summary = serializers.SerializerMethodField()
    must_have = serializers.SerializerMethodField()
    should_have = serializers.SerializerMethodField()
    could_have = serializers.SerializerMethodField()
    wont_have = serializers.SerializerMethodField()

    class Meta:
        model = MoscowScopeAnalysis
        fields = (
            "id",
            "idea_id",
            "summary",
            "must_have",
            "should_have",
            "could_have",
            "wont_have",
            "prompt_version",
            "provider",
            "model_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def _result_value(self, obj, key):
        return obj.result[key]

    def get_summary(self, obj):
        return self._result_value(obj, "summary")

    def get_must_have(self, obj):
        return self._result_value(obj, "must_have")

    def get_should_have(self, obj):
        return self._result_value(obj, "should_have")

    def get_could_have(self, obj):
        return self._result_value(obj, "could_have")

    def get_wont_have(self, obj):
        return self._result_value(obj, "wont_have")


class MomTestQuestionRequestSerializer(serializers.Serializer):
    question_count = serializers.IntegerField(
        required=False,
        default=10,
        min_value=8,
        max_value=10,
    )


class MomTestQuestionSerializer(serializers.Serializer):
    category = serializers.CharField()
    question = serializers.CharField()


class MomTestQuestionResponseSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    framework = serializers.CharField()
    question_count = serializers.IntegerField()
    questions = MomTestQuestionSerializer(many=True)

class MoscowResultSerializer(serializers.Serializer):
    must = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    should = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    could = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    wont = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )


class IdeaAnalysisResponseSerializer(serializers.Serializer):
    idea_summary = serializers.CharField()
    target_customer = serializers.CharField()
    problem_statement = serializers.CharField()
    value_proposition = serializers.CharField()

    risky_assumptions = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    mom_test_questions = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )

    moscow = MoscowResultSerializer()

    validation_roadmap = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    evidence_to_collect = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )

    final_recommendation = serializers.CharField()