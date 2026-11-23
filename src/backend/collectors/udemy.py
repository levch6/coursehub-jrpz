"""Збирач Udemy (CH-16).

Структура відповіді нижче є припущенням для базового каркаса. У задачі CH-16 її
потрібно звірити з реальними джерелами даних платформи.
"""

from typing import Any, ClassVar

from .base import PagedJsonCollector
from .dto import CourseDTO
from .parsing import normalize_language, normalize_level, to_decimal


class UdemyCollector(PagedJsonCollector):
    platform: ClassVar[str] = "udemy"
    endpoint: ClassVar[str] = "https://www.udemy.com/api/courses/"

    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        return list(payload.get("results", []))

    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        return CourseDTO(
            external_id=str(raw["id"]),
            title=raw["title"],
            description=raw.get("headline", ""),
            url="https://www.udemy.com" + raw["url"],
            category=raw.get("category"),
            price=to_decimal(raw.get("price")),
            rating=to_decimal(raw.get("avg_rating")),
            language=normalize_language(raw.get("locale")),
            level=normalize_level(raw.get("instructional_level")),
        )
