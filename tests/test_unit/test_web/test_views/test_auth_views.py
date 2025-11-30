from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from logger.setup import LoggingConfig
from authdrf.exc import EmailNotFound, InvalidPassword
from authdrf.web.views.auth_views import SignUpView, SignInView
from authdrf.service.auth_services import SignUpService
from authdrf.data.models.user_models import User
from tests.base_tests import BaseUserTest, BaseViewTestMixin, UserTestData


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
