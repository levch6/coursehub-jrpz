from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

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
        queryset = Favorite.objects.filter(user=self.request.user).select_related(
            "course__platform", "course__category"
        )
        if self.action == "list":
            # Курси, приховані адміністратором (ФВ-23), не показуються і в обраному,
            # але користувач і далі може прибрати такий запис зі свого обраного.
            queryset = queryset.filter(course__is_hidden=False)
        return queryset

    def create(self, request, *args, **kwargs):
        """Додає курс в обране: 201 для нового запису, 200, якщо курс уже там."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        code = status.HTTP_201_CREATED if serializer.created else status.HTTP_200_OK
        return Response(serializer.data, status=code)
