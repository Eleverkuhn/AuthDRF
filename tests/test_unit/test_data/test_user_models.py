from django.test import TestCase

from authdrf.exc import UserAlreadyExists
from authdrf.data.models.user_models import UserRepository
from tests.base_tests import UserTestData


class TestUserModel(TestCase):
    def test_create_user_with_the_same_email(self) -> None:
        model_data = UserTestData()._generate_user_model_data()
        UserRepository(model_data).create()
        with self.assertRaises(UserAlreadyExists):
            UserRepository(model_data).create()
