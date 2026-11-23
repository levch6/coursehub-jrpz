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
        value = _normalize_number_text(value)
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    # NaN і нескінченність не є коректною ціною чи рейтингом.
    return number if number.is_finite() else None


def _normalize_number_text(text: str) -> str:
    """Прибирає символи валют і розрізняє кому як роздільник тисяч або дробової частини.

    «1,299.99» дає «1299.99», «19,99» дає «19.99», «1,299» дає «1299».
    """
    text = text.replace("$", "").replace("€", "").replace(" ", "").strip()
    if "," in text and "." in text:
        return text.replace(",", "")
    if text.count(",") == 1 and len(text.split(",")[1]) <= 2:
        return text.replace(",", ".")
    return text.replace(",", "")


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
