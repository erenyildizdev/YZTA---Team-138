from django.urls import path

from .views import (
    IdeaAnalysisView,
    InterviewNoteDetailView,
    InterviewNoteListCreateView,
    MomTestQuestionGenerateView,
    MoscowScopeAnalysisView,
)

app_name = "analyses"

urlpatterns = [
    path(
        "analyze/",
        IdeaAnalysisView.as_view(),
        name="idea-analysis",
    ),
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
        "ideas/<int:idea_id>/interview-notes/",
        InterviewNoteListCreateView.as_view(),
        name="interview-note-list-create",
    ),
    path(
        "ideas/<int:idea_id>/interview-notes/<int:note_id>/",
        InterviewNoteDetailView.as_view(),
        name="interview-note-detail",
    ),
]
