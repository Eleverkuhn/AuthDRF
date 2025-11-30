from datetime import timedelta
from typing import override

from rest_framework.response import Response

from logger.setup import LoggingConfig
from authdrf.exc import EmailNotFound
from authdrf.service.jwt_services import JWTService
from authdrf.service.password_services import PasswordService
from authdrf.data.models.user_models import User, UserRepository


class BaseService:
    def __init__(self, request_data: dict) -> None:
        self.request_data = request_data


class SignUpService(BaseService):
    def exec(self) -> None:
        self.request_data.pop("confirm_password")
        UserRepository(self.request_data).create()

    @staticmethod
    def success_message() -> str:
        return "Your account has been successfully created"


class SignInService(BaseService):
    @override
    def __init__(self, response: Response, request_data: dict) -> None:
        super().__init__(request_data)
        self.response = response

    def exec(self) -> Response:
        user = self.verify_login_data()
        self.set_cookies(user.id)
        return self.response

    def verify_login_data(self) -> User:
        user = self.check_user_exists()
        PasswordService(
            password=self.request_data["password"],
            hashed_password=user.password
        ).verify()
        return user

    def check_user_exists(self) -> User:
        try:
            user = User.objects.get(email=self.request_data["email"])
        except User.DoesNotExist:
            raise EmailNotFound()
        else:
            return user

    def set_cookies(self, user_id: int) -> None:
        access_token, refresh_token = TokenService(user_id).exec()
        self.set_token_to_response(
            "access_token",
            access_token,
            TokenService.access_token_life()
        )
        self.set_token_to_response(
            "refresh_token",
            refresh_token,
            TokenService.refresh_token_life()
        )

    def set_token_to_response(
            self, cookie_key: str, token: str, age: int
    ) -> None:
        self.response.set_cookie(
            key=cookie_key,
            value=token,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=age
        )


class TokenService:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    @staticmethod
    def access_token_life() -> int:
        return int(timedelta(minutes=15).total_seconds())

    @staticmethod
    def refresh_token_life() -> int:
        return int(timedelta(days=7).total_seconds())

    def exec(self) -> tuple[str, str]:
        return (self.create_access_token(), self.create_refresh_token())

    def create_access_token(self) -> str:
        return JWTService().create(self.user_id, self.access_token_life())

    def create_refresh_token(self) -> str:
        return JWTService().create(self.user_id, self.refresh_token_life())
