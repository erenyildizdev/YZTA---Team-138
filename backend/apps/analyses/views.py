from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ideas.models import Idea

from .models import MoscowScopeAnalysis
from .serializers import (
    MomTestQuestionRequestSerializer,
    MomTestQuestionResponseSerializer,
    MoscowScopeAnalysisSerializer,
)
from .services import MoscowGenerationError, generate_mom_test_questions, generate_moscow_scope


class MomTestQuestionGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, idea_id, *args, **kwargs):
        request_serializer = MomTestQuestionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        idea = get_object_or_404(Idea.objects.filter(user=request.user), pk=idea_id)
        question_count = request_serializer.validated_data["question_count"]
        questions = generate_mom_test_questions(idea, question_count=question_count)

        response_serializer = MomTestQuestionResponseSerializer(
            data={
                "idea_id": idea.id,
                "framework": "the_mom_test",
                "question_count": question_count,
                "questions": questions,
            }
        )
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MoscowScopeAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_owned_idea(self, request, idea_id):
        return get_object_or_404(Idea.objects.filter(user=request.user), pk=idea_id)

    def get(self, request, idea_id, *args, **kwargs):
        idea = self._get_owned_idea(request, idea_id)
        analysis = get_object_or_404(MoscowScopeAnalysis, idea=idea)
        return Response(MoscowScopeAnalysisSerializer(analysis).data)

    def post(self, request, idea_id, *args, **kwargs):
        idea = self._get_owned_idea(request, idea_id)
        existed = MoscowScopeAnalysis.objects.filter(idea=idea).exists()
        try:
            analysis = generate_moscow_scope(idea)
        except MoscowGenerationError:
            return Response(
                {"detail": "The MoSCoW scope could not be generated."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        response_status = status.HTTP_200_OK if existed else status.HTTP_201_CREATED
        return Response(MoscowScopeAnalysisSerializer(analysis).data, status=response_status)
