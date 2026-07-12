from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ideas.models import Idea

from .serializers import MomTestQuestionRequestSerializer, MomTestQuestionResponseSerializer
from .services import generate_mom_test_questions


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
