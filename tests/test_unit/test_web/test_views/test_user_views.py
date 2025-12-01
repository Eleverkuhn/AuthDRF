from typing import override

from django.urls import reverse
from django.test import TestCase

from logger.setup import LoggingConfig
from authdrf.exc import UserAlreadyExists
from authdrf.web.views.user_views import UserPageView
from authdrf.data.models.user_models import User
from tests.base_tests import (
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
        BaseTestProtectedViewMixin, UserPageMixin, UserPageTestMixin
):
    template = UserPageView.template_name

    @override
    def setUp(self) -> None:
        super().setUp()
        self.response = self.client.get(self.url)

    def test_contains_user_info(self) -> None:
        self.check_contains()


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
