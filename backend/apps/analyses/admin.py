from django.contrib import admin

from .models import InterviewNote, MoscowScopeAnalysis


@admin.register(InterviewNote)
class InterviewNoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "idea",
        "interviewee_name",
        "interviewed_at",
        "created_at",
    )
    search_fields = (
        "interviewee_name",
        "interviewee_profile",
        "notes",
        "idea__title",
    )
    list_filter = ("interviewed_at", "created_at")


admin.site.register(MoscowScopeAnalysis)
