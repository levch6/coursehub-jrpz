"""Збирач Udemy (CH-16).

Структура відповіді нижче є припущенням для базового каркаса. У задачі CH-16 її
потрібно звірити з реальними джерелами даних платформи.
"""

from typing import Any, ClassVar
from urllib.parse import urljoin

from .base import PagedJsonCollector
from .dto import CourseDTO
from .parsing import detect_currency, normalize_language, normalize_level, to_decimal


class UdemyCollector(PagedJsonCollector):
    platform: ClassVar[str] = "udemy"
    endpoint: ClassVar[str] = "https://www.udemy.com/api/courses/"

    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        return list(payload.get("results", []))

    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        price = raw.get("price")
        path = raw["url"]
        # urljoin мовчки повернув би головну сторінку для порожнього значення.
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"порожня або некоректна адреса курсу: {path!r}")
        return CourseDTO(
            external_id=str(raw["id"]),
            title=raw["title"],
            description=raw.get("headline") or "",
            # urljoin коректно обробляє і відносні шляхи, і вже абсолютні адреси.
            url=urljoin("https://www.udemy.com/", path),
            category=raw.get("category") or None,
            price=to_decimal(price),
            # Валюту видно лише з символу в рядковій ціні, інакше вважаємо USD.
            currency=detect_currency(price) or "USD",
            rating=to_decimal(raw.get("avg_rating")),
            language=normalize_language(raw.get("locale")),
            level=normalize_level(raw.get("instructional_level")),
        )
