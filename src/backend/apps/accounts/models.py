"""Модель користувача: вхід за електронною поштою та роль (користувач або адміністратор)."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email: str | None) -> str:
        """Пошта зберігається в нижньому регістрі повністю, а не лише домен.

        Інакше адреси, що відрізняються лише регістром, дали б два облікові записи.
        """
        return super().normalize_email(email).strip().lower()

    def get_by_natural_key(self, username: str | None):
        # Вхід без урахування регістру; iexact знаходить і записи, створені до нормалізації.
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Електронна пошта є обов'язковою")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", User.Role.ADMIN)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "Користувач"
        ADMIN = "admin", "Адміністратор"

    username = None
    email = models.EmailField("електронна пошта", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN

    def __str__(self) -> str:
        return self.email
