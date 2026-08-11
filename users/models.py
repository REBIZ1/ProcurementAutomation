from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


USER_TYPE_CHOICES = (
    ("buyer", "Покупатель"),
    ("shop", "Поставщик"),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=150,
        validators=[username_validator],
        unique=True,
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=True,
    )
    company = models.CharField(
        verbose_name="Компания",
        max_length=100,
        blank=True,
    )
    position = models.CharField(
        verbose_name="Должность",
        max_length=100,
        blank=True,
    )
    type = models.CharField(
        verbose_name="Тип пользователя",
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default="buyer",
    )
    is_active = models.BooleanField(
        verbose_name="Аккаунт активирован",
        default=False,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    class Meta:
        ordering = ("email",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
