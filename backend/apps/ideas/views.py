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