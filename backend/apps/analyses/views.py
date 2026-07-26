from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ideas.models import Idea

from .models import (
    InterviewEvidenceAnalysis,
    InterviewNote,
    MoscowScopeAnalysis,
)

from .serializers import (
    IdeaAnalysisRequestSerializer,
    IdeaAnalysisResponseSerializer,
    InterviewEvidenceAnalysisSerializer,
    InterviewNoteSerializer,
    MomTestQuestionRequestSerializer,
    MomTestQuestionResponseSerializer,
    MoscowScopeAnalysisSerializer,
)

from .services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
)
from .services.analyzer import analyze_idea
from .services.llm_client import LLMClientError

from .services.interview_evidence import (
    InterviewNotesNotFoundError,
    analyze_interview_evidence,
)


def _get_owned_idea(request, idea_id):
    return get_object_or_404(
        Idea.objects.filter(user=request.user),
        pk=idea_id,
    )


def _get_owned_note(request, idea_id, note_id):
    idea = _get_owned_idea(request, idea_id)
    return get_object_or_404(
        InterviewNote.objects.filter(idea=idea),
        pk=note_id,
    )


class IdeaAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = IdeaAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = analyze_idea(
                serializer.validated_data["idea_text"]
            )
        except LLMClientError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response_serializer = IdeaAnalysisResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)

        return Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )

class MomTestQuestionGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, idea_id, *args, **kwargs):
        request_serializer = MomTestQuestionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        idea = get_object_or_404(
            Idea.objects.filter(user=request.user),
            pk=idea_id,
        )

        question_count = request_serializer.validated_data["question_count"]
        questions = generate_mom_test_questions(
            idea,
            question_count=question_count,
        )

        response_serializer = MomTestQuestionResponseSerializer(
            data={
                "idea_id": idea.id,
                "framework": "the_mom_test",
                "question_count": question_count,
                "questions": questions,
            }
        )
        response_serializer.is_valid(raise_exception=True)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class MoscowScopeAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_owned_idea(self, request, idea_id):
        return _get_owned_idea(request, idea_id)

    def get(self, request, idea_id, *args, **kwargs):
        idea = self._get_owned_idea(request, idea_id)
        analysis = get_object_or_404(
            MoscowScopeAnalysis,
            idea=idea,
        )

        return Response(
            MoscowScopeAnalysisSerializer(analysis).data
        )

    def post(self, request, idea_id, *args, **kwargs):
        idea = self._get_owned_idea(request, idea_id)
        existed = MoscowScopeAnalysis.objects.filter(idea=idea).exists()

        try:
            analysis = generate_moscow_scope(idea)
        except MoscowGenerationError:
            return Response(
                {
                    "detail": (
                        "The MoSCoW scope could not be generated."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_status = (
            status.HTTP_200_OK
            if existed
            else status.HTTP_201_CREATED
        )

        return Response(
            MoscowScopeAnalysisSerializer(analysis).data,
            status=response_status,
        )


class InterviewNoteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)
        notes = InterviewNote.objects.filter(idea=idea)

        return Response(
            InterviewNoteSerializer(notes, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)
        serializer = InterviewNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(idea=idea)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class InterviewNoteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, idea_id, note_id, *args, **kwargs):
        note = _get_owned_note(request, idea_id, note_id)
        return Response(
            InterviewNoteSerializer(note).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, idea_id, note_id, *args, **kwargs):
        note = _get_owned_note(request, idea_id, note_id)
        serializer = InterviewNoteSerializer(note, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, idea_id, note_id, *args, **kwargs):
        note = _get_owned_note(request, idea_id, note_id)
        serializer = InterviewNoteSerializer(
            note,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, idea_id, note_id, *args, **kwargs):
        note = _get_owned_note(request, idea_id, note_id)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InterviewEvidenceAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)

        analysis = (
            InterviewEvidenceAnalysis.objects
            .filter(idea=idea)
            .prefetch_related("interview_notes")
            .first()
        )

        if analysis is None:
            return Response(
                {
                    "detail": (
                        "Bu fikir için daha önce oluşturulmuş "
                        "bir görüşme analizi bulunamadı."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            InterviewEvidenceAnalysisSerializer(analysis).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)

        try:
            analysis = analyze_interview_evidence(idea)
        except InterviewNotesNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LLMClientError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            InterviewEvidenceAnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED,
        )
