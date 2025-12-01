from django.db import models
from django.db.utils import IntegrityError

from authdrf.exc import UserAlreadyExists
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
        try:
            user = User.objects.create(**self.model_data)
        except IntegrityError:
            raise UserAlreadyExists()
        else:
            return user

    def change_password(self, user_id: int) -> None:
        self.hash_password()
        user = User.objects.get(id=user_id)
        user.password = self.model_data["password"]
        user.save()

    def hash_password(self) -> None:
        hashed_password = PasswordService(self.model_data["password"]).hash()
        self.model_data["password"] = hashed_password
