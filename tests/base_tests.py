from typing import override

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from faker import Faker

from config.settings.dev import env
from authdrf.web.serializers.user_serializers import PersonalUserSerializer
from authdrf.service.auth_services import TokenService
from authdrf.data.models.user_models import User, UserRepository
from authdrf.data.models.permission_models import RoleRepository


class BaseUserTest:  # TODO: rename to 'BaseAuthTest'
    def setUp(self) -> None:
        super().setUp()
        self.request_data = UserTestData().generate_sign_up_data()


class BaseSignInTest:
    def setUp(self) -> None:
        super().setUp()
        self.request_data = UserTestData().generate_sign_in_data()


class UserTestData:
    def __init__(self) -> None:
        self.faker = Faker()

    def create_premium_subscriber(self) -> User:
        user = self.create_user()
        user.role = RoleRepository().premium_subscriber
        user.save()
        return user

    def create_subscriber(self) -> User:
        # user = UserRepository(self._generate_user_model_data()).create()
        user = self.create_user()
        user.role = RoleRepository().subscriber
        user.save()
        return user

    def create_user(self) -> User:
        return UserRepository(self._generate_user_model_data()).create()

    def generate_sign_in_data(self) -> dict[str, str]:
        user_model_data = self._generate_user_model_data()
        UserRepository(user_model_data).create()  # TODO: move this to 'TestWithCreatedUserMixin'
        sign_in_data = {
            "email": user_model_data["email"],
            "password": user_model_data["password"]
        }
        return sign_in_data

    def generate_sign_up_data(self) -> dict[str, str]:  # REF: merge this with base_user_data and password_data
        test_password = self._generate_password()
        test_data = {
            "first_name": self.faker.first_name(),
            "middle_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": self.faker.email(),
            "password": test_password,
            "confirm_password": test_password
        }
        return test_data

    def _generate_user_model_data(self) -> dict[str, str]:
        user_model_data = {
            **self._generate_base_user_data(),
            "password": self._generate_password()
        }
        return user_model_data

    def _generate_sign_in_data_with_no_user(self) -> dict[str, str]:
        sign_in_data = {
            "email": self.faker.email(),
            "password": self._generate_password()
        }
        return sign_in_data

    def _generate_base_user_data(self) -> dict[str, str]:
        base_user_data = {
            "first_name": self.faker.first_name(),
            "middle_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": self.faker.email(),
        }
        return base_user_data

    def _generate_password_data(self) -> dict[str, str]:
        password = self._generate_password()
        password_data = {
            "password": password,
            "confirm_password": password
        }
        return password_data

    def _generate_password(self) -> str:
        test_password = self.faker.password(
            length=10,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True
        )
        return test_password


class BaseViewTestMixin:
    url: str
    template: str

    def test_get_returns_200_OK(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_template_is_used(self) -> None:
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)


class TestWithCreatedUserMixin:
    def setUp(self) -> None:
        self.user = UserTestData().create_user()


class BasePermissionViewTest:
    fixtures = [
        f"{env.fixtures_dir}/permissions.json",
        f"{env.fixtures_dir}/roles.json"
    ]


class TestWithCreatedSubscriberMixin(BasePermissionViewTest):
    def setUp(self) -> None:
        self.user = UserTestData().create_subscriber()


class TestWithCreatedPremiumSubscriberMixin(BasePermissionViewTest):
    def setUp(self) -> None:
        self.user = UserTestData().create_premium_subscriber()


class UserPageMixin(TestWithCreatedUserMixin):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.personal_info = PersonalUserSerializer(self.user).data


class TestUpdatePersonalInfoMixin(UserPageMixin):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.personal_info.update({"email": UserTestData().faker.email()})


class ClientWithCookies:
    def set_cookies(self) -> None:
        response = Response()
        token_service = TokenService(response, self.user.id)
        self.client.cookies["access_token"] = token_service.access_token
        self.client.cookies["refresh_token"] = token_service.refresh_token


class BaseTestProtectedViewMixin(TestWithCreatedUserMixin, ClientWithCookies):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.set_cookies()


class TestSubscriberViewMixin(
        BaseViewTestMixin,
        TestWithCreatedSubscriberMixin,
        ClientWithCookies
):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.set_cookies()


class TestPremiumSubscriberViewMixin(
        BaseViewTestMixin,
        TestWithCreatedPremiumSubscriberMixin,
        ClientWithCookies
):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.set_cookies()


class APIClientProtectedMixin(BaseTestProtectedViewMixin, ClientWithCookies):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.set_cookies()
