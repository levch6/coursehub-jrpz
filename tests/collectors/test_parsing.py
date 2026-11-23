from decimal import Decimal

import pytest

from collectors.parsing import normalize_language, normalize_level, to_decimal


@pytest.mark.parametrize(
    ("value", "expected"),
    [("$19.99", Decimal("19.99")), (10, Decimal("10")), ("0", Decimal("0")), ("", None),
     (None, None), ("безкоштовно", None)],
)
def test_to_decimal(value, expected):
    assert to_decimal(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("Beginner", "beginner"), ("All Levels", "all"), ("Expert", "advanced"), (None, "all"),
     ("щось незрозуміле", "all")],
)
def test_normalize_level(value, expected):
    assert normalize_level(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("en_US", "en"), ("uk-UA", "uk"), (["fr", "en"], "fr"), ([], ""), (None, "")],
)
def test_normalize_language(value, expected):
    assert normalize_language(value) == expected
