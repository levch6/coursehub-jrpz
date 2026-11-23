"""Налаштування для робочого середовища (Google Cloud, за nginx)."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

# У робочому середовищі не можна працювати із запасним ключем з base.py:
# ним підписуються JWT і сесії, тому ключ має бути заданий явно.
if not os.environ.get("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured("Змінна середовища DJANGO_SECRET_KEY є обов'язковою для prod")
# Значення-заглушка з .env.example теж не підходить.
if os.environ["DJANGO_SECRET_KEY"] == "change-me":  # noqa: S105
    raise ImproperlyConfigured("DJANGO_SECRET_KEY має заглушку change-me: задайте справжній ключ")

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
