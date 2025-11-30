from typing import override

from django.test import TestCase
from rest_framework.response import Response

from authdrf.exc import EmailNotFound
from authdrf.service.auth_services import SignUpService, SignInService
from authdrf.data.models.user_models import User
from tests.base_tests import BaseUserTest, BaseSignInTest, UserTestData


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

    def test_check_user_returns_user_if_email_was_found(self) -> None:
        user = self.service.check_user_exists()
        self.assertEqual(user.email, self.request_data["email"])
