"""Моделі каталогу: платформа-джерело, категорія та курс."""

from django.db import models


class Platform(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    base_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Початковий"
        INTERMEDIATE = "intermediate", "Середній"
        ADVANCED = "advanced", "Просунутий"
        ALL = "all", "Усі рівні"

    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="courses")
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="courses"
    )
    external_id = models.CharField(max_length=200)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    language = models.CharField(max_length=10, blank=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL)
    # Відбиток нормалізованої назви допомагає шукати дублікати (ФВ-05).
    fingerprint = models.CharField(max_length=64, db_index=True, blank=True)
    is_available = models.BooleanField(default=True)  # ФВ-07
    is_hidden = models.BooleanField(default=False)  # ФВ-23
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "external_id"], name="uniq_course_per_platform"
            )
        ]

    def __str__(self) -> str:
        return self.title
