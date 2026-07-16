from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IdeaViewSet

app_name = "ideas"

router = DefaultRouter()
router.register(r"", IdeaViewSet, basename="idea")

urlpatterns = [
    path("", include(router.urls)),
]
