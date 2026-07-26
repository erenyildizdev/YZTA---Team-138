from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.analyses.services.analyzer import analyze_idea

from .mentor_agent import MentorAgentError, run_mentor_chat
from .models import Idea, RiskyAssumptions, ValidationRoadmap
from .serializers import IdeaSerializer, RiskyAssumptionsSerializer, ValidationRoadmapSerializer
from .services import (
    RiskyAssumptionsGenerationError,
    build_validation_roadmap_prompt,
    generate_risky_assumptions_payload,
    generate_validation_roadmap_payload,
)


class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Idea.objects.filter(user=self.request.user).order_by("-created_at")

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

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-roadmap")
    def generate_roadmap(self, request, pk=None):
        idea = self.get_object()
        build_validation_roadmap_prompt(idea)
        roadmap_data = generate_validation_roadmap_payload(idea)

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
            result = run_mentor_chat(idea, message, history)
        except MentorAgentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)