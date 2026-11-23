"""Контракт запису про курс, який приймає каталог.

Це структурний інтерфейс (Protocol): каталог нічого не знає про те, хто саме
створює записи. Будь-який об'єкт із цими атрибутами (наприклад, CourseDTO зі
збирачів) можна передати в репозиторій.
"""

from decimal import Decimal
from typing import Protocol


class CourseRecord(Protocol):
    external_id: str
    title: str
    url: str
    description: str
    category: str | None
    price: Decimal | None
    currency: str
    rating: Decimal | None
    language: str
    level: str
