from unittest import TestCase

from authdrf.exc import InvalidPassword
from authdrf.service.password_services import PasswordService
from tests.base_tests import UserTestData


class TestPasswordService(TestCase):
    def setUp(self) -> None:
        self.password = UserTestData()._generate_password()
        self.hashed_password = PasswordService(self.password).hash()

    def test_verify_raises_invalid_password_if_hash_does_not_match(self) -> None:
        with self.assertRaises(InvalidPassword):
            PasswordService("wrong", self.hashed_password).verify()

    def test_verify_passes_for_valid_hash(self) -> None:
        PasswordService(self.password, self.hashed_password)
