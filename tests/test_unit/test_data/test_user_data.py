from django.test import TestCase

from authdrf.exc import UserAlreadyExists
from authdrf.data.models.user_models import UserRepository
from tests.base_tests import UserTestData


class TestUserRepository(TestCase):
    def test_raises_already_exists_for_the_same_email(self) -> None:
        model_data = UserTestData()._generate_user_model_data()
        UserRepository(model_data).create()
        with self.assertRaises(UserAlreadyExists):
            UserRepository(model_data).create()

    def test_reactivates_account_if_existing_email_is_inactive(self) -> None:
        model_data = UserTestData()._generate_user_model_data()
        user = UserRepository(model_data).create()
        user.is_active = False
        user.save()

        new_data = UserTestData()._generate_user_model_data()
        new_data.update({"email": model_data["email"]})
        new_user = UserRepository(new_data).create()

        self.assertEqual(new_user.email, user.email)
        self.assertTrue(new_user.is_active)
        self.assertNotEqual(new_user.first_name, user.first_name)
