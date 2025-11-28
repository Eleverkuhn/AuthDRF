from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from authdrf.data.models.base_models import ModelFieldDefault


class CustomUserManager(BaseUserManager):
    def create_superuser(
            self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

    def create_user(
            self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=ModelFieldDefault.NAME_LENGTH)
    middle_name = models.CharField(max_length=ModelFieldDefault.NAME_LENGTH)
    last_name = models.CharField(max_length=ModelFieldDefault.NAME_LENGTH)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __repr__(self) -> str:
        return f"{self.email}"
