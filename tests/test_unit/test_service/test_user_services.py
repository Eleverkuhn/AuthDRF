from unittest import TestCase

from authdrf.exc import UserAlreadyExists
from authdrf.service.user_services import UserService
from authdrf.data.models.user_models import User
from tests.base_tests import TestUpdatePersonalInfoMixin, UserTestData


class TestUserService(TestUpdatePersonalInfoMixin, TestCase):
    def test_updates_personal_info(self) -> None:
        UserService(self.personal_info).update(self.user.id)
        user = User.objects.get(email=self.personal_info["email"])
        self.assertTrue(user)

    def test_raises_already_exists(self) -> None:
        another_user = UserTestData().create_user()
        self.personal_info["email"] = another_user.email
        with self.assertRaises(UserAlreadyExists):
            UserService(self.personal_info).update(self.user.id)

    def test_change_without_email(self) -> None:
        self.personal_info["first_name"] = UserTestData().faker.name()
        self.personal_info["email"] = self.user.email
        user = UserService(self.personal_info).update(self.user.id)
        self.assertNotEqual(user.first_name, self.user.first_name)
