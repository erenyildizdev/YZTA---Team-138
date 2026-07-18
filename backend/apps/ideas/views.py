from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Idea, ValidationRoadmap
from .serializers import IdeaSerializer, ValidationRoadmapSerializer
from .services import build_validation_roadmap_prompt, generate_validation_roadmap_payload


class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Idea.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        idea_id = response.data.get("id")
        response.data = {
            "message": "Idea saved successfully.",
            "idea": response.data,
            "analysis_url": f"/analysis/{idea_id}" if idea_id else None,
        }
        return Response(response.data, status=status.HTTP_201_CREATED)

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