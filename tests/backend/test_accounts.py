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


def test_register_rejects_password_similar_to_email(api):
    response = api.post(
        "/api/auth/register/", {"email": "johnsmith2024@example.com", "password": "johnsmith2024"}
    )
    assert response.status_code == 400
    assert "password" in response.data


def test_register_stores_email_in_lowercase(api):
    response = api.post(
        "/api/auth/register/", {"email": "New.User@Example.COM", "password": "StrongPass123"}
    )
    assert response.status_code == 201
    assert get_user_model().objects.get().email == "new.user@example.com"


def test_register_rejects_email_differing_only_by_case(api, user):
    response = api.post(
        "/api/auth/register/", {"email": "USER@Example.com", "password": "StrongPass123"}
    )
    assert response.status_code == 400
    assert get_user_model().objects.count() == 1


def test_login_ignores_email_case(api, user):
    response = api.post(
        "/api/auth/token/", {"email": "User@EXAMPLE.com", "password": "StrongPass123"}
    )
    assert response.status_code == 200


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
