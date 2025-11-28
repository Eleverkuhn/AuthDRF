from django.test import TestCase

from authdrf.service.auth_services import SignUpService
from authdrf.data.models.user_models import User
from tests.base_tests import UserTestData


class TestSignUpService(TestCase):
    def setUp(self) -> None:
        self.request_data = UserTestData().generate()

    def test_exec_creates_user(self) -> None:
        SignUpService(self.request_data).exec()
        user_db = User.objects.get(email=self.request_data["email"])
        self.assertTrue(user_db)
