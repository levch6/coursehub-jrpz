from decimal import Decimal

import pytest

from collectors.parsing import (
    detect_currency,
    normalize_language,
    normalize_level,
    to_decimal,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("$19.99", Decimal("19.99")),
        (10, Decimal("10")),
        ("0", Decimal("0")),
        ("", None),
        (None, None),
        ("безкоштовно", None),
        ("1,299.99", Decimal("1299.99")),
        ("19,99", Decimal("19.99")),
        ("1,299", Decimal("1299")),
        ("1.299,99", Decimal("1299.99")),
        ("€1.299,99", Decimal("1299.99")),
        ("1\u00a0299,99", Decimal("1299.99")),
        ("1\u202f299,99 €", Decimal("1299.99")),
        ("NaN", None),
        ("Infinity", None),
    ],
)
def test_to_decimal(value, expected):
    assert to_decimal(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Beginner", "beginner"),
        ("All Levels", "all"),
        ("Expert", "advanced"),
        (None, "all"),
        ("щось незрозуміле", "all"),
    ],
)
def test_normalize_level(value, expected):
    assert normalize_level(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("en_US", "en"),
        ("uk-UA", "uk"),
        (["fr", "en"], "fr"),
        ([], ""),
        (None, ""),
        ("English", "en"),
        ("Ukrainian", "uk"),
        ("Spanish", "es"),
        ("Chinese", "zh"),
        ("Klingon", ""),
    ],
)
def test_normalize_language(value, expected):
    assert normalize_language(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("$19.99", "USD"), ("€19,99", "EUR"), ("19,99 €", "EUR"), ("19.99", None), (19.99, None)],
)
def test_detect_currency(value, expected):
    assert detect_currency(value) == expected
