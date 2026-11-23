import pytest

from apps.favorites.models import Favorite

pytestmark = pytest.mark.django_db


def test_favorites_require_authentication(api):
    assert api.get("/api/favorites/").status_code == 401


def test_add_and_list_favorite(auth_api, user, course):
    response = auth_api.post("/api/favorites/", {"course_id": course.pk})
    assert response.status_code == 201
    listing = auth_api.get("/api/favorites/")
    assert listing.data["count"] == 1
    assert listing.data["results"][0]["course"]["id"] == course.pk
    assert Favorite.objects.filter(user=user).count() == 1


def test_adding_twice_does_not_duplicate(auth_api, user, course):
    auth_api.post("/api/favorites/", {"course_id": course.pk})
    auth_api.post("/api/favorites/", {"course_id": course.pk})
    assert Favorite.objects.filter(user=user).count() == 1


def test_remove_favorite(auth_api, user, course):
    favorite = Favorite.objects.create(user=user, course=course)
    assert auth_api.delete(f"/api/favorites/{favorite.pk}/").status_code == 204
    assert not Favorite.objects.exists()


def test_cannot_see_other_users_favorites(auth_api, admin_user, course):
    Favorite.objects.create(user=admin_user, course=course)
    assert auth_api.get("/api/favorites/").data["count"] == 0
