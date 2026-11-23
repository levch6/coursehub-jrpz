"""Кореневі маршрути серверного застосунку."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    """Перевірка доступності сервісу для моніторингу та Docker (НФВ-06)."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/favorites/", include("apps.favorites.urls")),
    path("api/admin/", include("apps.administration.urls")),
    path("api/", include("apps.catalog.urls")),
]
