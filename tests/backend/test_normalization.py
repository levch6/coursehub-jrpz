from apps.catalog.normalization import make_fingerprint, normalize_text


def test_normalize_text_removes_punctuation_case_and_extra_spaces():
    assert normalize_text("  Python:  The   Complete Guide! ") == "python the complete guide"


def test_normalize_text_removes_diacritics():
    assert normalize_text("Café Déjà Vu") == "cafe deja vu"


def test_same_title_gives_same_fingerprint():
    assert make_fingerprint("Learn Python!", "en") == make_fingerprint("learn  python", "EN")


def test_language_changes_fingerprint():
    assert make_fingerprint("Learn Python", "en") != make_fingerprint("Learn Python", "uk")
