from django.db import models
from django.db.utils import IntegrityError

from authdrf.exc import UserAlreadyExists
from authdrf.service.password_services import PasswordService
from authdrf.data.models.base_models import ModelFieldDefault
from authdrf.data.models.permission_models import Role


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
    # password = models.BinaryField()
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, related_name="users", null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __repr__(self) -> str:
        return f"{self.email}"


class UserRepository:  # TODO: move this to separate module
    def __init__(self, model_data: dict[str, str | bytes]) -> None:
        self.model_data = model_data.copy()

    def create(self) -> User:
        try:
            user = User.objects.get(email=self.model_data["email"])
        except User.DoesNotExist:
            user = self.create_new_user()
            return user
        else:
            self.check_is_active(user)
            self.reactivate_user(user)
            return user

    def create_new_user(self) -> User:
        self.hash_password()
        user = User.objects.create(**self.model_data)
        return user

    def check_is_active(self, user: User) -> None:
        if user.is_active:
            raise UserAlreadyExists()

    def reactivate_user(self, user: User) -> None:
        self.hash_password()
        user.is_active = True
        self.update(user, self.model_data)

    @staticmethod
    def update(user: User, update_data: dict) -> None:
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
            user.save()
        except IntegrityError:
            raise UserAlreadyExists()

    def change_password(self, user_id: int) -> None:
        self.hash_password()
        user = User.objects.get(id=user_id)
        user.password = self.model_data["password"]
        user.save()

    @staticmethod
    def set_is_active_to_false(user_id: int) -> None:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()

    def hash_password(self) -> None:
        hashed_password = PasswordService(self.model_data["password"]).hash()
        self.model_data["password"] = hashed_password
