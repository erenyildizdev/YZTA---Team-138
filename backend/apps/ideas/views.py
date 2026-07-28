import unicodedata
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.analyses.services.analyzer import analyze_idea
from apps.analyses.services.llm_client import LLMClientError

from .mentor_agent import MentorAgentError, run_mentor_chat
from .models import CompetitorAnalysis, GeneralEvaluation, Idea, InvestorPitch, RiskyAssumptions, ValidationRoadmap
from .serializers import (
    CompetitorAnalysisSerializer,
    GeneralEvaluationSerializer,
    IdeaSerializer,
    InvestorPitchSerializer,
    RiskyAssumptionsSerializer,
    ValidationRoadmapSerializer,
)
from .services import (
    CompetitorAnalysisGenerationError,
    GeneralEvaluationGenerationError,
    InvestorPitchGenerationError,
    RiskyAssumptionsGenerationError,
    RoadmapGenerationError,
    generate_competitor_analysis_payload,
    generate_general_evaluation_payload,
    generate_investor_pitch_payload,
    generate_risky_assumptions_payload,
    generate_validation_roadmap_payload,
)


def _summarize_general_evaluation(idea) -> str:
    if not hasattr(idea, "general_evaluation"):
        return ""

    evaluation_data = idea.general_evaluation.evaluation_data or {}
    strengths = evaluation_data.get("strengths") or []
    next_action = evaluation_data.get("next_action") or ""

    sentences = []
    if strengths:
        sentences.append(strengths[0])
    if next_action:
        sentences.append(next_action)

    return " ".join(
        sentence if sentence.endswith((".", "!", "?")) else f"{sentence}."
        for sentence in sentences
    )


class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Idea.objects.filter(user=self.request.user)
            .select_related(
                "risky_assumptions",
                "mom_test_questions_analysis",
                "moscow_scope_analysis",
                "validation_roadmap",
                "general_evaluation",
                "competitor_analysis",
                "investor_pitch",
            )
            .order_by("-created_at", "-id")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="compare")
    def compare(self, request):
        ids_param = request.query_params.get("ids", "")
        try:
            ids = [int(value) for value in ids_param.split(",") if value.strip()]
        except ValueError:
            return Response(
                {"detail": "ids parametresi geçersiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not ids:
            return Response(
                {"detail": "Karşılaştırmak için en az bir fikir id'si belirtmelisin."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ideas_by_id = {idea.id: idea for idea in self.get_queryset().filter(id__in=ids)}
        ordered_ideas = [ideas_by_id[idea_id] for idea_id in ids if idea_id in ideas_by_id]

        results = []
        for idea in ordered_ideas:
            assumptions = []
            if hasattr(idea, "risky_assumptions"):
                assumptions = idea.risky_assumptions.assumptions_data.get("assumptions", [])

            moscow_counts = {"must_have": 0, "should_have": 0, "could_have": 0, "wont_have": 0}
            if hasattr(idea, "moscow_scope_analysis"):
                moscow_result = idea.moscow_scope_analysis.result or {}
                for key in moscow_counts:
                    moscow_counts[key] = len(moscow_result.get(key, []) or [])

            results.append(
                {
                    "id": idea.id,
                    "title": idea.title,
                    "sector": idea.sector,
                    "target_audience": idea.target_audience,
                    "analysis_status": IdeaSerializer(idea).data["analysis_status"],
                    "created_at": idea.created_at,
                    "risky_assumptions": {
                        "total": len(assumptions),
                        "validated": sum(1 for a in assumptions if a.get("status") == "validated"),
                        "refuted": sum(1 for a in assumptions if a.get("status") == "refuted"),
                        "untested": sum(1 for a in assumptions if a.get("status") == "untested"),
                        "high_risk": sum(1 for a in assumptions if a.get("level") == "high"),
                    },
                    "moscow": moscow_counts,
                    "mom_test_question_count": (
                        len(idea.mom_test_questions_analysis.questions)
                        if hasattr(idea, "mom_test_questions_analysis")
                        else 0
                    ),
                    "interview_note_count": idea.interview_notes.count(),
                    "competitor_analysis_summary": (
                        idea.competitor_analysis.analysis_data.get("differentiation", "")
                        if hasattr(idea, "competitor_analysis")
                        else ""
                    ),
                    "general_evaluation_summary": _summarize_general_evaluation(idea),
                }
            )

        return Response({"ideas": results}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="analyze")
    def analyze(self, request, pk=None):
        idea = self.get_object()

        idea_text = "\n".join(
            [
                f"Title: {idea.title}",
                f"Description: {idea.description}",
                f"Target audience: {idea.target_audience}",
                f"Problem: {idea.problem}",
                f"Solution: {idea.solution}",
                f"Sector: {idea.sector}",
            ]
        )

        result = analyze_idea(idea_text=idea_text)

        idea.rag_sources = result.get("sources", [])
        idea.save(update_fields=["rag_sources"])

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-roadmap")
    def generate_roadmap(self, request, pk=None):
        idea = self.get_object()

        try:
            roadmap_data = generate_validation_roadmap_payload(idea)
        except RoadmapGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        roadmap, _ = ValidationRoadmap.objects.update_or_create(
            idea=idea,
            defaults={"roadmap_data": roadmap_data},
        )

        serializer = ValidationRoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="roadmap")
    def roadmap(self, request, pk=None):
        idea = self.get_object()

        try:
            roadmap = idea.validation_roadmap
        except ValidationRoadmap.DoesNotExist:
            return Response({"detail": "Roadmap not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ValidationRoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-risky-assumptions")
    def generate_risky_assumptions(self, request, pk=None):
        idea = self.get_object()

        try:
            assumptions_data = generate_risky_assumptions_payload(idea)
        except RiskyAssumptionsGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assumptions, _ = RiskyAssumptions.objects.update_or_create(
            idea=idea,
            defaults={"assumptions_data": assumptions_data},
        )

        serializer = RiskyAssumptionsSerializer(assumptions)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="risky-assumptions")
    def risky_assumptions(self, request, pk=None):
        idea = self.get_object()

        try:
            assumptions = idea.risky_assumptions
        except RiskyAssumptions.DoesNotExist:
            return Response({"detail": "Risky assumptions not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RiskyAssumptionsSerializer(assumptions)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-evaluation")
    def generate_evaluation(self, request, pk=None):
        idea = self.get_object()

        try:
            evaluation_data = generate_general_evaluation_payload(idea)
        except GeneralEvaluationGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        evaluation, _ = GeneralEvaluation.objects.update_or_create(
            idea=idea,
            defaults={"evaluation_data": evaluation_data},
        )

        serializer = GeneralEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="evaluation")
    def evaluation(self, request, pk=None):
        idea = self.get_object()

        try:
            evaluation = idea.general_evaluation
        except GeneralEvaluation.DoesNotExist:
            return Response({"detail": "Evaluation not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GeneralEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-competitor-analysis")
    def generate_competitor_analysis(self, request, pk=None):
        idea = self.get_object()

        try:
            analysis_data = generate_competitor_analysis_payload(idea)
        except CompetitorAnalysisGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        analysis, _ = CompetitorAnalysis.objects.update_or_create(
            idea=idea,
            defaults={"analysis_data": analysis_data},
        )

        serializer = CompetitorAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="competitor-analysis")
    def competitor_analysis(self, request, pk=None):
        idea = self.get_object()

        try:
            analysis = idea.competitor_analysis
        except CompetitorAnalysis.DoesNotExist:
            return Response({"detail": "Competitor analysis not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompetitorAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-pitch")
    def generate_pitch(self, request, pk=None):
        idea = self.get_object()

        try:
            pitch_data = generate_investor_pitch_payload(idea)
        except InvestorPitchGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        pitch, _ = InvestorPitch.objects.update_or_create(
            idea=idea,
            defaults={"pitch_data": pitch_data},
        )

        serializer = InvestorPitchSerializer(pitch)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="pitch")
    def pitch(self, request, pk=None):
        idea = self.get_object()

        try:
            pitch = idea.investor_pitch
        except InvestorPitch.DoesNotExist:
            return Response({"detail": "Investor pitch not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorPitchSerializer(pitch)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="mentor-chat")
    def mentor_chat(self, request, pk=None):
        idea = self.get_object()

        message = str(request.data.get("message") or "").strip()
        if not message:
            return Response(
                {"detail": "message alanı boş olamaz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        history = request.data.get("history") or []
        if not isinstance(history, list):
            history = []

        try:
            result = run_mentor_chat(
                idea,
                message,
                history,
            )
        except (MentorAgentError, LLMClientError) as exc:
            return Response(
                {
                    "detail": str(exc)
                    or "AI servisine şu anda ulaşılamıyor."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            return Response(
                {
                    "detail": (
                        "AI servisine şu anda ulaşılamıyor. "
                        "Lütfen daha sonra tekrar deneyin."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )