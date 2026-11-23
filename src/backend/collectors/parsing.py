"""Допоміжні функції розбору значень, спільні для збирачів різних платформ."""

import re
from decimal import Decimal, InvalidOperation
from typing import Any

_LEVEL_ALIASES = {
    "beginner": "beginner",
    "introductory": "beginner",
    "all levels": "all",
    "all": "all",
    "intermediate": "intermediate",
    "advanced": "advanced",
    "expert": "advanced",
}

_CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR"}

# Звичайний, нерозривний (U+00A0) і вузький нерозривний (U+202F) пробіли
# трапляються як роздільники тисяч.
_SPACES = (" ", " ", " ")

# Повні назви мов, які деякі платформи (зокрема edX) віддають замість кодів ISO 639-1.
_LANGUAGE_NAMES = {
    "english": "en",
    "ukrainian": "uk",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "portuguese": "pt",
    "chinese": "zh",
    "italian": "it",
    "polish": "pl",
    "japanese": "ja",
    "arabic": "ar",
    "hindi": "hi",
}
_LANGUAGE_CODE = re.compile(r"[a-z]{2,3}")


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


def detect_currency(text: Any) -> str | None:
    """Визначає валюту за символом у рядку ціни: «$» дає USD, «€» дає EUR.

    Якщо символу немає або значення не є рядком, повертає None.
    """
    if not isinstance(text, str):
        return None
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in text:
            return code
    return None


def _normalize_number_text(text: str) -> str:
    """Прибирає символи валют і пробіли та визначає десятковий роздільник.

    Якщо є і кома, і крапка, десятковим вважається той роздільник, що стоїть
    останнім: «1,299.99» дає «1299.99», «1.299,99» дає «1299.99». Одна кома з
    одною-двома цифрами після неї є дробовою частиною («19,99»), інакше
    роздільником тисяч («1,299» дає «1299»).
    """
    for symbol in _CURRENCY_SYMBOLS:
        text = text.replace(symbol, "")
    for space in _SPACES:
        text = text.replace(space, "")
    text = text.strip()
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            return text.replace(".", "").replace(",", ".")
        return text.replace(",", "")
    if text.count(",") == 1 and len(text.split(",")[1]) <= 2:
        return text.replace(",", ".")
    return text.replace(",", "")


def normalize_level(value: Any) -> str:
    key = str(value or "").strip().lower()
    return _LEVEL_ALIASES.get(key, "all")


def normalize_language(value: Any) -> str:
    """Повертає код мови ISO 639-1 або порожній рядок, якщо мову не розпізнано.

    «en_US» і «en-GB» перетворює на «en», «English» на «en»; список бере за
    першим елементом. Невідому повну назву мови перетворює на порожній рядок.
    """
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    text = str(value or "").strip().lower()
    if text in _LANGUAGE_NAMES:
        return _LANGUAGE_NAMES[text]
    code = text.replace("_", "-").split("-")[0]
    return code if _LANGUAGE_CODE.fullmatch(code) else ""
