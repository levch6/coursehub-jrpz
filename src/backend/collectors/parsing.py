"""Допоміжні функції розбору значень, спільні для збирачів різних платформ."""

from decimal import Decimal, InvalidOperation
from typing import Any

from .dto import LEVELS

_LEVEL_ALIASES = {
    "beginner": "beginner",
    "introductory": "beginner",
    "all levels": "all",
    "all": "all",
    "intermediate": "intermediate",
    "advanced": "advanced",
    "expert": "advanced",
}


def to_decimal(value: Any) -> Decimal | None:
    """Перетворює число або рядок виду «$19.99» на Decimal; порожнє значення дає None."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.replace("$", "").replace("€", "").replace(",", ".").strip()
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def normalize_level(value: Any) -> str:
    key = str(value or "").strip().lower()
    level = _LEVEL_ALIASES.get(key, "all")
    return level if level in LEVELS else "all"


def normalize_language(value: Any) -> str:
    """«en_US» і «en-GB» перетворює на «en»; список бере за першим елементом."""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    text = str(value or "").strip().lower()
    return text.replace("_", "-").split("-")[0]
