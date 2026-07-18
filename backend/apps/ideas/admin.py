from django.contrib import admin

from .models import Idea


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "sector_category", "created_at")
    search_fields = ("title", "description", "target_audience", "problem", "solution", "sector_category")
