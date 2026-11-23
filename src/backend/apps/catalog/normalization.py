"""Нормалізація тексту та відбиток назви курсу для пошуку дублікатів (ФВ-05)."""

import hashlib
import re
import unicodedata

_NON_WORD = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Нижній регістр, без діакритики й розділових знаків, зі стислими пробілами."""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    without_punct = _NON_WORD.sub(" ", stripped)
    return _SPACES.sub(" ", without_punct).strip()


def make_fingerprint(title: str, language: str = "") -> str:
    """Стабільний відбиток курсу: однакові назви мовою дають однаковий відбиток."""
    payload = f"{normalize_text(title)}|{language.strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
