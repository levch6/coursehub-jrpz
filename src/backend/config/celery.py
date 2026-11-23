"""Налаштування Celery: черга задач на базі Redis і планувальник Celery Beat."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("coursehub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
