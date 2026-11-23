"""Журнал запусків збору даних (ФВ-06)."""

from django.db import models

from apps.catalog.models import Platform


class ScrapeRun(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "У черзі"
        RUNNING = "running", "Виконується"
        SUCCESS = "success", "Успішно"
        FAILED = "failed", "Помилка"

    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    courses_created = models.PositiveIntegerField(default=0)
    courses_updated = models.PositiveIntegerField(default=0)
    courses_unavailable = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.platform.slug}: {self.status}"
