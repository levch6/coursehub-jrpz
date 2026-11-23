"""Збирач edX (CH-24).

Структура відповіді є припущенням для базового каркаса; її буде уточнено в CH-24.
"""

from typing import Any, ClassVar

from .base import PagedJsonCollector
from .dto import CourseDTO
from .parsing import normalize_language, normalize_level


class EdxCollector(PagedJsonCollector):
    platform: ClassVar[str] = "edx"
    endpoint: ClassVar[str] = "https://discovery.edx.org/api/v1/courses/"

    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        return list(payload.get("objects", []))

    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        return CourseDTO(
            external_id=raw["key"],
            title=raw["title"],
            description=raw.get("short_description", ""),
            url=raw["marketing_url"],
            category=raw.get("subject"),
            language=normalize_language(raw.get("language")),
            level=normalize_level(raw.get("level_type")),
        )
