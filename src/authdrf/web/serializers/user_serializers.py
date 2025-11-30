from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from authdrf.data.models.user_models import User


class BuiltInPasswordValidator:
    def __call__(self, value) -> None:
        validate_password(value)


class PasswordMatchesValidator:
    requires_context = True

    def __init__(self, password_field: str) -> None:
        self.password_field = password_field

    def __call__(self, value: str, confirm_password_field) -> None:
        password = confirm_password_field.parent.initial_data.get(
            self.password_field
        )
        if not password == value:
            raise ValidationError("Password do not match")


class BasePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        validators=[BuiltInPasswordValidator()],
        help_text=""
    )


class SignInSerializer(BasePasswordSerializer):
    email = serializers.EmailField(help_text="example@email.com")


class PasswordSerializer(BasePasswordSerializer):
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[PasswordMatchesValidator("password")],
        help_text=""
    )


class UserSerializer(serializers.ModelSerializer, PasswordSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())],
        help_text="example@email.com"
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "confirm_password"
        ]
