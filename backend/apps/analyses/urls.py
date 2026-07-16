from django.urls import path

from .views import (
    IdeaAnalysisView,
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
]