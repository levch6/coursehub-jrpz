import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured


def _import_prod_settings():
    # base.py читає змінні середовища під час імпорту, тому імпортуємо обидва модулі заново.
    for name in ("config.settings.prod", "config.settings.base"):
        sys.modules.pop(name, None)
    return importlib.import_module("config.settings.prod")


def test_prod_settings_require_secret_key(monkeypatch):
    monkeypatch.delenv("DJANGO_SECRET_KEY", raising=False)
    with pytest.raises(ImproperlyConfigured):
        _import_prod_settings()


def test_prod_settings_reject_placeholder_secret_key(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "change-me")
    with pytest.raises(ImproperlyConfigured):
        _import_prod_settings()


def test_prod_settings_use_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", "a-real-secret-from-the-environment")
    prod = _import_prod_settings()
    assert prod.SECRET_KEY == "a-real-secret-from-the-environment"
    assert prod.DEBUG is False
