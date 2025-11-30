from django.db import models

from authdrf.service.password_services import PasswordService
from authdrf.data.models.base_models import ModelFieldDefault


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=ModelFieldDefault.NAME_LENGTH,
        help_text="John"
    )
    middle_name = models.CharField(
        max_length=ModelFieldDefault.NAME_LENGTH,
        help_text="Michael"
    )
    last_name = models.CharField(
        max_length=ModelFieldDefault.NAME_LENGTH,
        help_text="Doe"
    )
    password = models.BinaryField()
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __repr__(self) -> str:
        return f"{self.email}"


class UserRepository:  # TODO: move this to separate module
    def __init__(self, model_data: dict[str, str | bytes]) -> None:
        self.model_data = model_data.copy()

    def create(self) -> User:
        self.hash_password()
        user = User.objects.create(**self.model_data)
        return user

    def hash_password(self) -> None:
        hashed_password = PasswordService(self.model_data["password"]).hash()
        self.model_data["password"] = hashed_password
