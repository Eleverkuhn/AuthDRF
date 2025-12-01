from time import sleep
from typing import override

from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.response import Response

from logger.setup import LoggingConfig
from authdrf.exc import (
    EmailNotFound, AuthorizationError, RefreshRequired, UserDoesNotExist
)
from authdrf.service.auth_services import (
    SignUpService, SignInService, AuthorizationService, RefreshTokenService
)
from authdrf.service.jwt_services import JWTService
from authdrf.data.models.user_models import User
from tests.base_tests import (
    BaseUserTest, BaseSignInTest, UserTestData, TestWithCreatedUserMixin
)


class TestSignUpService(BaseUserTest, TestCase):
    def test_exec_creates_user(self) -> None:
        SignUpService(self.request_data).exec()
        user_db = User.objects.get(email=self.request_data["email"])
        self.assertTrue(user_db)


class TestSignInService(BaseSignInTest, TestCase):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.service = SignInService(Response(), self.request_data)

    def test_exec(self) -> None:
        self.service.exec()

    def test_check_user_exists_raises_email_not_found(self) -> None:
        request_data = UserTestData()._generate_sign_in_data_with_no_user()
        self.service.request_data = request_data
        with self.assertRaises(EmailNotFound):
            self.service.check_user_exists()

    def test_raises_user_does_not_exist_if_user_is_not_active(self) -> None:
        user = User.objects.get(email=self.request_data["email"])
        user.is_active = False
        user.save()
        with self.assertRaises(UserDoesNotExist):
            SignInService(Response(), self.request_data).exec()

    def test_check_user_returns_user_if_email_was_found(self) -> None:
        user = self.service.check_user_exists()
        self.assertEqual(user.email, self.request_data["email"])


class TestRefreshTokenService(TestWithCreatedUserMixin, TestCase):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.request = RequestFactory()
        self.response = Response()

    def test_cookies_are_set(self) -> None:
        refresh_token = JWTService().create(self.user.id, 600)
        self.request.COOKIES = {"refresh_token": refresh_token}

        response = RefreshTokenService(self.request, self.response).exec()
        self.assertTrue(response.cookies.get("access_token"))
        self.assertTrue(response.cookies.get("refresh_token"))

    def test_returns_unauthorized_response_if_refresh_token_invalid(self) -> None:
        self.request.COOKIES = {"refresh_token": "invalid"}

        response = RefreshTokenService(self.request, self.response).exec()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            AuthorizationError.default_message, response.content.decode()
        )


class TestAuthoriztionService(TestCase):
    def test_exec_returns_user_if_checks_are_passed(self) -> None:
        test_user = UserTestData().create_user()
        token = JWTService().create(test_user.id, 600)
        cookies = {"access_token": token, "refresh_token": token}
        user = AuthorizationService(cookies).exec()
        self.assertEqual(test_user.id, user.id)

    def test_raises_authorization_error_if_no_access_token(self) -> None:
        with self.assertRaises(AuthorizationError):
            AuthorizationService({}).check_access_token_exists()

    def test_check_access_token_exists_passes_if_access_token(self) -> None:
        cookies = {"access_token": "mock"}
        AuthorizationService(cookies).check_access_token_exists

    def test_raises_authorization_error_if_no_refresh_token(self) -> None:
        with self.assertRaises(AuthorizationError):
            AuthorizationService({}).check_access_token_exists()

    def test_check_refresh_exists_passes_if_refresh_token(self) -> None:
        cookies = {"refresh_token": "mock"}
        AuthorizationService(cookies).check_access_token_exists

    def test_raises_authorization_error_if_token_invalid(self) -> None:
        cookies = {"access_token": "invalid_token"}
        with self.assertRaises(AuthorizationError):
            AuthorizationService(cookies).check_access_token_is_valid()

    def test_raises_refresh_required_error_if_token_expired(self) -> None:
        token = JWTService().create(1, 1)
        cookies = {"access_token": token}
        sleep(2)
        with self.assertRaises(RefreshRequired):
            AuthorizationService(cookies).check_access_token_is_valid()

    def test_raises_authorization_error_if_payload_invalid(self) -> None:
        payload = {"not_id": 1}
        with self.assertRaises(AuthorizationError):
            AuthorizationService({}).check_payload_contains_user_id(payload)

    def test_check_user_exists_raises_authorization_error_if_no_user(self) -> None:
        with self.assertRaises(AuthorizationError):
            AuthorizationService({}).check_user_exists(1)
