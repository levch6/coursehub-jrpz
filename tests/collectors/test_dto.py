from decimal import Decimal

import pytest

from collectors import CourseDTO


def make(**overrides) -> CourseDTO:
    data = {"external_id": "1", "title": "Python", "url": "https://example.com/p"}
    data.update(overrides)
    return CourseDTO(**data)


def test_minimal_dto_has_defaults():
    dto = make()
    assert dto.currency == "USD"
    assert dto.level == "all"
    assert dto.price is None


def test_dto_is_immutable():
    with pytest.raises(AttributeError):
        make().title = "Інша назва"


@pytest.mark.parametrize(
    "overrides",
    [
        {"external_id": ""},
        {"title": "   "},
        {"url": "/relative"},
        {"price": Decimal("-1")},
        {"rating": Decimal("5.1")},
        {"level": "godlike"},
    ],
)
def test_invalid_data_is_rejected(overrides):
    with pytest.raises(ValueError):
        make(**overrides)
