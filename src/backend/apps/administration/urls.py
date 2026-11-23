from django.urls import path

from .views import CourseModerationView, ScrapeRunListView, StatsView, TriggerCollectionView

urlpatterns = [
    path("stats/", StatsView.as_view(), name="admin-stats"),
    path("collection/runs/", ScrapeRunListView.as_view(), name="admin-runs"),
    path(
        "collection/<slug:platform>/run/",
        TriggerCollectionView.as_view(),
        name="admin-collection-run",
    ),
    path("courses/<int:pk>/", CourseModerationView.as_view(), name="admin-course"),
]
