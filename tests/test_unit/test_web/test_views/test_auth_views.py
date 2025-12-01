from time import sleep
from typing import override

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from logger.setup import LoggingConfig
from authdrf.exc import (
    EmailNotFound, InvalidPassword, AuthorizationError, UserAlreadyExists
)
from authdrf.web.views.auth_views import SignUpView, SignInView
from authdrf.service.auth_services import SignUpService
from authdrf.service.jwt_services import JWTService
from authdrf.data.models.user_models import User
from tests.base_tests import (
    BaseUserTest,
    BaseViewTestMixin,
    UserTestData,
    BaseTestProtectedViewMixin,
    TestWithCreatedUserMixin
)


class TestSignUpView(BaseUserTest, BaseViewTestMixin, TestCase):
    url = reverse("sign_up")
    template = SignUpView.template_name

    def test_creates_new_user(self) -> None:
        self.client.post(self.url, data=self.request_data)
        created_user = User.objects.get(email=self.request_data["email"])
        self.assertTrue(created_user)

    def test_redirects_to_main_page_on_succeed(self) -> None:
        response = self.client.post(
            self.url, data=self.request_data, follow=False
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("main"))

    def test_main_page_contains_succeed_message_after_redirection(self) -> None:
        response = self.client.post(self.url, self.request_data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            SignUpService.success_message(),
            response.content.decode()
        )

    def test_contains_error_message_if_already_exists_was_raised(self) -> None:
        self.client.post(self.url, self.request_data)
        response = self.client.post(self.url, self.request_data)
        self.assertIn(
            UserAlreadyExists.default_message, response.content.decode()
        )


class TestSignInView(BaseViewTestMixin, TestCase):
    url = reverse("sign_in")
    template = SignInView.template_name

    def setUp(self) -> None:
        self.request_data = UserTestData().generate_sign_in_data()

    def test_cookies_are_set(self) -> None:
        response = self.client.post(
            self.url, data=self.request_data, follow=False
        )
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_response_contains_email_not_found_error_message(self) -> None:
        request_data = UserTestData()._generate_sign_in_data_with_no_user()
        response = self.client.post(self.url, data=request_data)
        self.assertIn(EmailNotFound.default_message, response.content.decode())

    def test_response_contains_invalid_password_error_message(self) -> None:
        self.request_data["password"] = "invalid password"
        response = self.client.post(self.url, data=self.request_data)
        self.assertIn(InvalidPassword.default_message, response.content.decode())

    def test_redirect_to_user_page_on_succeed(self) -> None:
        response = self.client.post(
            self.url, data=self.request_data, follow=False
        )
        self.assertEqual(response["Location"], reverse("user_page"))


class TestRefreshTokenView(TestWithCreatedUserMixin, TestCase):
    url = reverse("refresh")

    def test_redirects_to_originally_requested_url_on_succeed(self) -> None:
        refresh_token = JWTService().create(self.user.id, 600)
        self.client.cookies["refresh_token"] = refresh_token
        url = "".join([self.url, f"?next={reverse('main')}"])

        response = self.client.get(url, follow=False)

        self.assertEqual(response["Location"], reverse("main"))


class TestProtectedView(TestWithCreatedUserMixin, TestCase):
    url = reverse("user_page")

    def test_unlogged_in_user_can_not_view_content(self) -> None:
        response = self.client.get(self.url)
        self.assertIn(
            AuthorizationError.default_message,
            response.content.decode()
        )

    def test_expired_access_token_redirects_to_refresh_view(self) -> None:
        expired_access_token = JWTService().create(self.user.id, 1)
        refresh_token = JWTService().create(self.user.id, 600)
        self.client.cookies["access_token"] = expired_access_token
        self.client.cookies["refresh_token"] = refresh_token
        sleep(2)

        response = self.client.get(self.url, follow=False)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("refresh"))
