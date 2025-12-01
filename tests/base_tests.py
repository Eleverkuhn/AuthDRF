from rest_framework import status
from rest_framework.response import Response
from faker import Faker

from authdrf.service.auth_services import TokenService
from authdrf.data.models.user_models import User, UserRepository


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


class BaseTestProtectedViewMixin(TestWithCreatedUserMixin):
    def setUp(self) -> None:
        super().setUp()
        self.set_cookies()

    def set_cookies(self) -> None:
        response = Response()
        token_service = TokenService(response, self.user.id)
        self.client.cookies["access_token"] = token_service.access_token
        self.client.cookies["refresh_token"] = token_service.refresh_token
