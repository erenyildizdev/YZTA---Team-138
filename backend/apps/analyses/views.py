import logging

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import content_disposition_header
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ideas.models import Idea

from .models import (
    InterviewEvidenceAnalysis,
    InterviewNote,
    MomTestQuestionsAnalysis,
    MoscowScopeAnalysis,
    ValidationWorkflowRun,
)

from .serializers import (
    InterviewEvidenceAnalysisSerializer,
    InterviewNoteSerializer,
    MomTestQuestionRequestSerializer,
    MomTestQuestionResponseSerializer,
    MoscowScopeAnalysisSerializer,
    ValidationWorkflowFailureResponseSerializer,
    ValidationWorkflowRequestSerializer,
    ValidationWorkflowRunSerializer,
    ValidationWorkflowSuccessResponseSerializer,
)

from .services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
)
from .services.llm_client import LLMClientError
from .services.validation_workflow import (
    INTERNAL_ERROR,
    ValidationWorkflowError,
    run_validation_workflow,
)
from .services.workflow_runs import (
    WorkflowRunAlreadyRunning,
    WorkflowRunIdentityMismatch,
    WorkflowRunProgressRecorder,
    acquire_workflow_run,
)

from .services.interview_evidence import (
    InterviewNotesNotFoundError,
    analyze_interview_evidence,
)
from .services.report_pdf import (
    build_report_filename,
    build_report_pdf,
)


logger = logging.getLogger(__name__)


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


class ValidationReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, idea_id, *args, **kwargs):
        idea = get_object_or_404(
            Idea.objects.filter(user=request.user).select_related(
                "risky_assumptions",
                "mom_test_questions_analysis",
                "moscow_scope_analysis",
                "validation_roadmap",
                "general_evaluation",
                "competitor_analysis",
                "investor_pitch",
            ),
            pk=idea_id,
        )

        try:
            pdf_content = build_report_pdf(idea)
            filename = build_report_filename(idea)
        except Exception:
            logger.exception(
                "Validation report PDF generation failed for idea_id=%s.",
                idea.pk,
            )
            return Response(
                {
                    "detail": (
                        "PDF raporu oluşturulamadı. "
                        "Lütfen daha sonra tekrar deneyin."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(
            pdf_content,
            content_type="application/pdf",
        )
        response["Content-Disposition"] = content_disposition_header(
            True,
            filename,
        )
        response["Cache-Control"] = "private, no-store"
        return response


class ValidationWorkflowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)
        request_serializer = ValidationWorkflowRequestSerializer(
            data=request.data
        )
        request_serializer.is_valid(raise_exception=True)

        try:
            acquisition = acquire_workflow_run(
                idea,
                request_serializer.validated_data.get("run_id"),
            )
        except WorkflowRunAlreadyRunning as exc:
            return Response(
                {
                    "detail": (
                        "Bu fikir için bir analiz akışı zaten devam ediyor."
                    ),
                    "code": "workflow_already_running",
                    "run_id": str(exc.run_id),
                },
                status=status.HTTP_409_CONFLICT,
            )
        except WorkflowRunIdentityMismatch:
            raise Http404 from None

        workflow_run = acquisition.run
        if not acquisition.should_execute:
            if (
                isinstance(workflow_run.terminal_response, dict)
                and workflow_run.terminal_status_code is not None
            ):
                return Response(
                    workflow_run.terminal_response,
                    status=workflow_run.terminal_status_code,
                )
            return Response(
                {
                    "detail": "Bu analiz akışı daha önce tamamlandı.",
                    "code": "workflow_run_finished",
                    "run_id": str(workflow_run.pk),
                },
                status=status.HTTP_409_CONFLICT,
            )

        progress_recorder = WorkflowRunProgressRecorder(workflow_run.pk)

        try:
            workflow_result = run_validation_workflow(
                idea,
                progress_callback=progress_recorder,
            )
        except ValidationWorkflowError as exc:
            response_data = exc.as_response()
            response_data["run_id"] = workflow_run.pk
            response_serializer = ValidationWorkflowFailureResponseSerializer(
                data=response_data
            )
            response_serializer.is_valid(raise_exception=True)
            response_status = (
                status.HTTP_500_INTERNAL_SERVER_ERROR
                if exc.error_code == INTERNAL_ERROR
                else status.HTTP_502_BAD_GATEWAY
            )
            progress_recorder.finalize_failure(
                failed_stage=exc.failed_step,
                error_code=exc.error_code,
                response_data=dict(response_serializer.data),
                response_status_code=response_status,
            )
            return Response(
                response_serializer.data,
                status=response_status,
            )

        response_data = workflow_result.as_response()
        response_data["run_id"] = workflow_run.pk
        response_serializer = ValidationWorkflowSuccessResponseSerializer(
            data=response_data
        )
        response_serializer.is_valid(raise_exception=True)
        progress_recorder.finalize_success(
            dict(response_serializer.data),
            status.HTTP_200_OK,
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class ValidationWorkflowRunView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, run_id, *args, **kwargs):
        workflow_run = get_object_or_404(
            ValidationWorkflowRun.objects.filter(
                idea__user=request.user,
            ),
            pk=run_id,
        )
        return Response(
            ValidationWorkflowRunSerializer(workflow_run).data,
            status=status.HTTP_200_OK,
        )


class MomTestQuestionGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, idea_id, *args, **kwargs):
        idea = _get_owned_idea(request, idea_id)
        analysis = get_object_or_404(MomTestQuestionsAnalysis, idea=idea)
        questions = analysis.questions if isinstance(analysis.questions, list) else []
        return Response(
            {
                "idea_id": idea.id,
                "framework": "the_mom_test",
                "question_count": len(questions),
                "questions": questions,
            },
            status=status.HTTP_200_OK,
        )

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
        MomTestQuestionsAnalysis.objects.update_or_create(
            idea=idea,
            defaults={"questions": questions},
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
