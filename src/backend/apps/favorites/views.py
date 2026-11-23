from rest_framework import mixins, permissions, viewsets

from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Обране поточного користувача: перегляд, додавання, видалення."""

    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends: list = []

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            "course__platform", "course__category"
        )
