from typing import override

from django.urls import reverse
from django.test import TestCase, Client

from logger.setup import LoggingConfig
from authdrf.exc import UserAlreadyExists, AuthorizationError, UserDoesNotExist
from authdrf.web.views.user_views import UserPageView, ChangePasswordView
from authdrf.data.models.user_models import User
from tests.base_tests import (
    BaseViewTestMixin,
    BaseTestProtectedViewMixin,
    UserPageMixin,
    TestUpdatePersonalInfoMixin,
    APIClientProtectedMixin,
    UserTestData
)


class UserPageTestMixin(TestCase):
    url = reverse("user_page")

    def check_contains(self) -> None:
        for value in self.personal_info.values():
            self.assertIn(value, self.response.content.decode())


class TestUserPageView(
        BaseTestProtectedViewMixin,
        UserPageMixin,
        UserPageTestMixin,
        BaseViewTestMixin
):
    template = UserPageView.template_name

    @override
    def setUp(self) -> None:
        super().setUp()
        self.response = self.client.get(self.url)

    def test_contains_user_info(self) -> None:
        self.check_contains()

    def test_delete_redirects_to_main_page(self) -> None:
        response = self.client.delete(self.url, follow=False)
        self.assertEqual(response["Location"], reverse("main"))

    def test_delete_signs_out_user(self) -> None:
        self.client.delete(self.url)
        response = self.client.get(reverse("user_page"))
        self.assertIn(
            AuthorizationError.default_message, response.content.decode()
        )

    def test_user_can_not_login_after_deletion(self) -> None:
        sign_in_data = UserTestData().generate_sign_in_data()
        self.client.post(reverse("sign_in"), data=sign_in_data)
        self.client.delete(self.url)

        response = self.client.post(reverse("sign_in"), data=sign_in_data)

        self.assertIn(UserDoesNotExist.default_message, response.content.decode())


class TestUserPagePUT(
        APIClientProtectedMixin,
        TestUpdatePersonalInfoMixin,
        UserPageTestMixin,
):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.response = self.client.put(
            self.url, data=self.personal_info, format="json"
        )

    def test_put_updates_info(self) -> None:
        user = User.objects.get(email=self.personal_info["email"])
        self.assertEqual(self.user.id, user.id)

    def test_updated_info_displayed(self) -> None:
        self.check_contains()

    def test_displays_error_if_already_exists_was_raised(self) -> None:
        another_user = UserTestData().create_user()
        self.personal_info["email"] = another_user.email
        response = self.client.put(
            self.url, data=self.personal_info, format="json"
        )
        self.assertIn(UserAlreadyExists.default_message, response.content.decode())


class ChangePasswordTestMixin(TestCase):
    url = reverse("change_password")


class TestChangePasswordView(
        BaseTestProtectedViewMixin, BaseViewTestMixin, ChangePasswordTestMixin
):
    template = ChangePasswordView.template_name


class TestChangePasswordPUT(APIClientProtectedMixin, ChangePasswordTestMixin):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.new_password = UserTestData()._generate_password()
        self.request_data = {
            "password": self.new_password,
            "confirm_password": self.new_password
        }

    def test_updates_password(self) -> None:
        self.client.put(self.url, data=self.request_data, format="json")

        client = Client()
        sign_in_data = {"email": self.user.email, "password": self.new_password}
        response = client.post(
            reverse("sign_in"), data=sign_in_data, follow=False
        )
        self.assertEqual(response["Location"], reverse("user_page"))

    def test_user_is_signed_out_after_password_change(self) -> None:
        self.client.put(self.url, data=self.request_data, format="json")
        response = self.client.get(reverse("user_page"))
        self.assertIn(
            AuthorizationError.default_message, response.content.decode()
        )
