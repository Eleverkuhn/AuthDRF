from unittest import TestCase

from logger.setup import LoggingConfig
from authdrf.service.user_services import UserService
from authdrf.data.models.user_models import User
from tests.base_tests import UserPageMixin, UserTestData, TestUpdatePersonalInfoMixin


class TestUserService(TestUpdatePersonalInfoMixin, TestCase):
    def test_updates_personal_info(self) -> None:
        # self.personal_info.update({"email": UserTestData().faker.email()})

        UserService(self.personal_info).update(self.user.id)

        user = User.objects.get(email=self.personal_info["email"])
        self.assertTrue(user)
