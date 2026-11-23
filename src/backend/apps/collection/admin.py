from django.contrib import admin

from .models import ScrapeRun


@admin.register(ScrapeRun)
class ScrapeRunAdmin(admin.ModelAdmin):
    list_display = ("platform", "status", "started_at", "courses_created", "courses_updated")
    list_filter = ("platform", "status")
