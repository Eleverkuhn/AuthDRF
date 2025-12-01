from datetime import timedelta
from typing import override

from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from authdrf.exc import (
    EmailNotFound, AuthorizationError, JWTError, ExpiredToken, RefreshRequired
)
from authdrf.service.jwt_services import JWTService, Payload
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
        TokenService(self.response, user.id).set_cookies()
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


class RefreshTokenService:
    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response
        self.cookies = request.COOKIES

    def exec(self) -> Response:
        try:
            user_id = self.get_user_id_from_payload()
        except AuthorizationError as error:
            response = render(
                self.request,
                "response_401.xhtml",
                {"error": str(error)},
                status=status.HTTP_401_UNAUTHORIZED
            )
            return response
        else:
            TokenService(self.response, user_id).set_cookies()
            return self.response

    def get_user_id_from_payload(self) -> int:
        # TODO: create separate classes for checking
        authorization_service = AuthorizationService(self.cookies)
        authorization_service.check_refresh_token_exists()
        payload = authorization_service.check_refresh_token_is_valid()
        user_id = payload["id"]
        authorization_service.check_user_exists(user_id)
        return user_id


class TokenService:
    def __init__(self, response: Response, user_id: int) -> None:
        self.response = response
        self.user_id = user_id

    @property
    def access_token(self) -> str:
        return JWTService().create(self.user_id, self.access_token_life())

    @staticmethod
    def access_token_life() -> int:
        return int(timedelta(minutes=15).total_seconds())

    @property
    def refresh_token(self) -> str:
        return JWTService().create(self.user_id, self.refresh_token_life())

    @staticmethod
    def refresh_token_life() -> int:
        return int(timedelta(days=7).total_seconds())

    def set_cookies(self) -> None:
        self.set_token_to_response(
            "access_token",
            self.access_token,
            TokenService.access_token_life()
        )
        self.set_token_to_response(
            "refresh_token",
            self.refresh_token,
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


class AuthorizationService:
    def __init__(self, cookies: dict) -> None:
        self.cookies = cookies

    @property
    def access_token(self) -> str | None:
        return self.cookies.get("access_token")

    @property
    def refresh_token(self) -> str | None:
        return self.cookies.get("refresh_token")

    def exec(self) -> User:
        self.check_cookies_content()
        payload = self.check_access_token_is_valid()
        self.check_payload_contains_user_id(payload)
        user = self.check_user_exists(payload["id"])
        return user

    def check_cookies_content(self) -> None:
        self.check_access_token_exists()
        self.check_refresh_token_exists()

    def check_access_token_exists(self) -> None:
        if not self.access_token:
            raise AuthorizationError()

    def check_refresh_token_exists(self) -> None:
        if not self.refresh_token:
            raise AuthorizationError()

    def check_access_token_is_valid(self) -> Payload:
        try:
            payload = JWTService().verify(self.access_token)
        except ExpiredToken:
            raise RefreshRequired()
        except JWTError:
            raise AuthorizationError()
        else:
            return payload

    def check_refresh_token_is_valid(self) -> Payload:
        try:
            payload = JWTService().verify(self.refresh_token)
        except JWTError:
            raise AuthorizationError()
        else:
            self.check_payload_contains_user_id(payload)
            return payload

    def check_payload_contains_user_id(self, payload: Payload) -> None:
        if not payload.get("id"):
            raise AuthorizationError()

    def check_user_exists(self, user_id: int) -> User:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthorizationError()
        else:
            return user
