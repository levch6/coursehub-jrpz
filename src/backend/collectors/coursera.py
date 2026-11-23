"""Збирач Coursera (CH-17).

Структура відповіді є припущенням для базового каркаса; її буде уточнено в CH-17.
"""

from typing import Any, ClassVar

from .base import PagedJsonCollector
from .dto import CourseDTO
from .parsing import normalize_language, normalize_level


class CourseraCollector(PagedJsonCollector):
    platform: ClassVar[str] = "coursera"
    endpoint: ClassVar[str] = "https://api.coursera.org/api/courses.v1"
    page_param: ClassVar[str] = "start"
    page_size_param: ClassVar[str] = "limit"
    offset_pagination: ClassVar[bool] = True

    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        return list(payload.get("elements", []))

    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        return CourseDTO(
            external_id=str(raw["id"]),
            title=raw["name"],
            description=raw.get("description", ""),
            url=f"https://www.coursera.org/learn/{raw['slug']}",
            category=(raw.get("domainTypes") or [{}])[0].get("domainId"),
            price=None,  # багато курсів Coursera безкоштовні для перегляду
            language=normalize_language(raw.get("primaryLanguages")),
            level=normalize_level(raw.get("level")),
        )
