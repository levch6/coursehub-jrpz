"""Побудова реєстру джерел за шляхом із налаштувань (ін'єкція залежності)."""

from django.conf import settings
from django.utils.module_loading import import_string

from .ports import SourceProvider


def load_sources() -> SourceProvider:
    factory = import_string(settings.COLLECTION_SOURCES_FACTORY)
    return factory()
