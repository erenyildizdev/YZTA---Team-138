import unicodedata
from collections.abc import Mapping

from rest_framework import serializers

from .models import (
    InterviewEvidenceAnalysis,
    InterviewNote,
    MoscowScopeAnalysis,
)
from .services.validation_workflow_contract import (
    WORKFLOW_ERROR_CODES,
    WORKFLOW_STEP_ORDER,
)


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


class ValidationWorkflowStepResultSerializer(StrictFieldsSerializer):
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=("completed",))
    result = serializers.JSONField()

    def validate_name(self, value):
        if value not in WORKFLOW_STEP_ORDER:
            raise serializers.ValidationError("Unknown workflow step.")
        return value


class ValidationWorkflowSuccessResponseSerializer(StrictFieldsSerializer):
    idea_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=("completed",))
    completed_steps = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    steps = ValidationWorkflowStepResultSerializer(
        many=True,
        allow_empty=False,
    )

    def validate(self, attrs):
        expected_steps = list(WORKFLOW_STEP_ORDER)
        completed_steps = attrs["completed_steps"]
        response_steps = [
            step["name"]
            for step in attrs["steps"]
        ]

        if completed_steps != expected_steps:
            raise serializers.ValidationError(
                {"completed_steps": "All workflow steps must be completed in order."}
            )
        if response_steps != completed_steps:
            raise serializers.ValidationError(
                {"steps": "Step results must match completed_steps in order."}
            )
        return attrs


class ValidationWorkflowFailureResponseSerializer(StrictFieldsSerializer):
    idea_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=("failed",))
    completed_steps = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )
    failed_step = serializers.CharField()
    error_code = serializers.ChoiceField(
        choices=WORKFLOW_ERROR_CODES
    )
    detail = serializers.CharField()
    steps = ValidationWorkflowStepResultSerializer(
        many=True,
        allow_empty=True,
    )

    def validate(self, attrs):
        workflow_steps = list(WORKFLOW_STEP_ORDER)
        completed_steps = attrs["completed_steps"]
        expected_completed_steps = workflow_steps[:len(completed_steps)]
        response_steps = [
            step["name"]
            for step in attrs["steps"]
        ]

        if completed_steps != expected_completed_steps:
            raise serializers.ValidationError(
                {"completed_steps": "Completed steps must follow workflow order."}
            )
        if len(completed_steps) >= len(workflow_steps):
            raise serializers.ValidationError(
                {"failed_step": "A completed workflow cannot have a failed step."}
            )
        if attrs["failed_step"] != workflow_steps[len(completed_steps)]:
            raise serializers.ValidationError(
                {"failed_step": "failed_step must be the next workflow step."}
            )
        if response_steps != completed_steps:
            raise serializers.ValidationError(
                {"steps": "Step results must match completed_steps in order."}
            )
        return attrs


class InterviewNoteSerializer(serializers.ModelSerializer):
    idea_id = serializers.IntegerField(read_only=True)
    interviewee_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    interviewee_profile = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    notes = serializers.CharField(
        max_length=10_000,
        allow_blank=False,
        trim_whitespace=True,
    )
    interviewed_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = InterviewNote
        fields = (
            "id",
            "idea_id",
            "interviewee_name",
            "interviewee_profile",
            "notes",
            "interviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "idea_id",
            "created_at",
            "updated_at",
        )

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            forbidden_fields = {"idea", "idea_id"}.intersection(data)
            if forbidden_fields:
                raise serializers.ValidationError(
                    {
                        field: "This field may not be provided."
                        for field in sorted(forbidden_fields)
                    }
                )

        return super().to_internal_value(data)

class InterviewEvidenceResultSerializer(StrictFieldsSerializer):
    supporting_evidence = serializers.ListField(
        child=serializers.CharField(
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=True,
    )
    contradicting_evidence = serializers.ListField(
        child=serializers.CharField(
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=True,
    )
    repeated_needs = serializers.ListField(
        child=serializers.CharField(
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=True,
    )
    new_risky_assumptions = serializers.ListField(
        child=serializers.CharField(
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=True,
    )
    next_validation_steps = serializers.ListField(
        child=serializers.CharField(
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=False,
    )

class InterviewEvidenceAnalysisSerializer(serializers.ModelSerializer):
    idea_id = serializers.IntegerField(read_only=True)
    interview_note_ids = serializers.PrimaryKeyRelatedField(
        source="interview_notes",
        many=True,
        read_only=True,
    )
    supporting_evidence = serializers.SerializerMethodField()
    contradicting_evidence = serializers.SerializerMethodField()
    repeated_needs = serializers.SerializerMethodField()
    new_risky_assumptions = serializers.SerializerMethodField()
    next_validation_steps = serializers.SerializerMethodField()

    class Meta:
        model = InterviewEvidenceAnalysis
        fields = (
            "id",
            "idea_id",
            "interview_note_ids",
            "supporting_evidence",
            "contradicting_evidence",
            "repeated_needs",
            "new_risky_assumptions",
            "next_validation_steps",
            "prompt_version",
            "provider",
            "model_name",
            "created_at",
        )
        read_only_fields = fields

    def _result_value(self, obj, key):
        value = obj.result.get(key, [])
        return value if isinstance(value, list) else []

    def get_supporting_evidence(self, obj):
        return self._result_value(obj, "supporting_evidence")

    def get_contradicting_evidence(self, obj):
        return self._result_value(obj, "contradicting_evidence")

    def get_repeated_needs(self, obj):
        return self._result_value(obj, "repeated_needs")

    def get_new_risky_assumptions(self, obj):
        return self._result_value(obj, "new_risky_assumptions")

    def get_next_validation_steps(self, obj):
        return self._result_value(obj, "next_validation_steps")


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

