"""Права доступу на основі ролі користувача (НФВ-13, ФВ-20)."""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Дозволяє доступ лише користувачам із роллю «Адміністратор»."""

    message = "Потрібна роль адміністратора."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin_role)
