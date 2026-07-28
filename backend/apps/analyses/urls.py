from django.urls import path

from .views import (
    InterviewEvidenceAnalysisView,
    InterviewNoteDetailView,
    InterviewNoteListCreateView,
    MomTestQuestionGenerateView,
    MoscowScopeAnalysisView,
    ValidationWorkflowView,
)

app_name = "analyses"

urlpatterns = [
    path(
        "ideas/<int:idea_id>/mom-test-questions/",
        MomTestQuestionGenerateView.as_view(),
        name="mom-test-question-generate",
    ),
    path(
        "ideas/<int:idea_id>/moscow-scope/",
        MoscowScopeAnalysisView.as_view(),
        name="moscow-scope",
    ),
    path(
        "ideas/<int:idea_id>/workflow/",
        ValidationWorkflowView.as_view(),
        name="validation-workflow",
    ),
    path(
        "ideas/<int:idea_id>/interview-notes/",
        InterviewNoteListCreateView.as_view(),
        name="interview-note-list-create",
    ),
    path(
        "ideas/<int:idea_id>/interview-notes/<int:note_id>/",
        InterviewNoteDetailView.as_view(),
        name="interview-note-detail",
    ),
    path(
        "ideas/<int:idea_id>/interview-evidence-analysis/",
        InterviewEvidenceAnalysisView.as_view(),
        name="interview-evidence-analysis",
    ),
]
