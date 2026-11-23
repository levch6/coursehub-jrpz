import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_register_creates_user_with_default_role(api):
    response = api.post(
        "/api/auth/register/", {"email": "new@example.com", "password": "StrongPass123"}
    )
    assert response.status_code == 201
    created = get_user_model().objects.get(email="new@example.com")
    assert created.role == "user"
    assert created.check_password("StrongPass123")
    assert "password" not in response.data


def test_register_rejects_weak_password(api):
    response = api.post("/api/auth/register/", {"email": "a@example.com", "password": "12345678"})
    assert response.status_code == 400


def test_register_rejects_duplicate_email(api, user):
    response = api.post("/api/auth/register/", {"email": user.email, "password": "StrongPass123"})
    assert response.status_code == 400


def test_login_returns_jwt_pair(api, user):
    response = api.post("/api/auth/token/", {"email": user.email, "password": "StrongPass123"})
    assert response.status_code == 200
    assert {"access", "refresh"} <= set(response.data)


def test_profile_requires_authentication(api):
    assert api.get("/api/auth/me/").status_code == 401


def test_profile_returns_current_user(auth_api, user):
    response = auth_api.get("/api/auth/me/")
    assert response.status_code == 200
    assert response.data["email"] == user.email


def test_superuser_has_admin_role(admin_user):
    assert admin_user.is_admin_role
