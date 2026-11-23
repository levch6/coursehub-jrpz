"""Службові кінцеві точки для адміністратора (ФВ-04, ФВ-06, ФВ-20, ФВ-23, ФВ-24)."""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from apps.catalog.models import Course, Platform
from apps.collection.models import ScrapeRun
from apps.collection.providers import load_sources
from apps.collection.tasks import run_collection

from .serializers import CourseModerationSerializer, ScrapeRunSerializer

User = get_user_model()


class StatsView(APIView):
    """Загальна статистика системи (ФВ-24)."""

    permission_classes = [IsAdminRole]

    def get(self, _request):
        return Response(
            {
                "courses": Course.objects.count(),
                "courses_available": Course.objects.filter(is_available=True).count(),
                "platforms": Platform.objects.count(),
                "users": User.objects.count(),
                "runs": ScrapeRun.objects.count(),
            }
        )


class ScrapeRunListView(generics.ListAPIView):
    """Журнал збору даних (ФВ-06)."""

    permission_classes = [IsAdminRole]
    serializer_class = ScrapeRunSerializer
    queryset = ScrapeRun.objects.select_related("platform")


class TriggerCollectionView(APIView):
    """Ручний запуск оновлення даних однієї платформи (ФВ-04)."""

    permission_classes = [IsAdminRole]

    def post(self, _request, platform: str):
        if platform not in load_sources().names():
            return Response({"detail": "Невідома платформа."}, status=status.HTTP_404_NOT_FOUND)
        task = run_collection.delay(platform)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class CourseModerationView(generics.UpdateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CourseModerationSerializer
    queryset = Course.objects.all()
    http_method_names = ["patch", "put", "options"]
