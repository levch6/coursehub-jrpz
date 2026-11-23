"""Єдиний формат запису про курс, який повертають усі збирачі (CourseDTO).

Об'єкт незмінний і перевіряє себе під час створення, тому некоректні дані не
потрапляють далі в конвеєр. Поля збігаються з контрактом ``CourseRecord``
каталогу, отже DTO можна передавати в репозиторій без перетворень.
"""

from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlparse

LEVELS = {"beginner", "intermediate", "advanced", "all"}
_STR_FIELDS = ("external_id", "title", "url", "description", "currency", "language", "level")


@dataclass(frozen=True, slots=True)
class CourseDTO:
    external_id: str
    title: str
    url: str
    description: str = ""
    category: str | None = None
    price: Decimal | None = None
    currency: str = "USD"
    rating: Decimal | None = None
    language: str = ""
    level: str = "all"

    def __post_init__(self) -> None:
        for name in _STR_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, str):
                raise ValueError(f"{name} має бути рядком, отримано {type(value).__name__}")
        if self.category is not None and not isinstance(self.category, str):
            raise ValueError("category має бути рядком або None")
        if not self.external_id.strip():
            raise ValueError("external_id не може бути порожнім")
        if not self.title.strip():
            raise ValueError("title не може бути порожнім")
        parsed_url = urlparse(self.url)
        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            raise ValueError(f"url має бути абсолютним: {self.url!r}")
        if self.price is not None and self.price < 0:
            raise ValueError("price не може бути від'ємною")
        if self.rating is not None and not Decimal(0) <= self.rating <= Decimal(5):
            raise ValueError("rating має бути в межах від 0 до 5")
        if self.level not in LEVELS:
            raise ValueError(f"невідомий рівень: {self.level!r}")
