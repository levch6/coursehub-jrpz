"""Збирачі даних про курси з платформ-джерел.

Пакет не залежить від Django: його можна тестувати та запускати окремо.
"""

from .base import CourseCollector, PagedJsonCollector
from .dto import CourseDTO
from .errors import CollectorError, FetchError, ParseError, UnknownPlatformError
from .fetching import Fetcher, RequestsFetcher
from .registry import CollectorRegistry, build_default_registry

__all__ = [
    "CollectorError",
    "CollectorRegistry",
    "CourseCollector",
    "CourseDTO",
    "Fetcher",
    "FetchError",
    "PagedJsonCollector",
    "ParseError",
    "RequestsFetcher",
    "UnknownPlatformError",
    "build_default_registry",
]
