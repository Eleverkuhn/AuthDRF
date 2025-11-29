from unittest import TestCase

from rest_framework.validators import ValidationError

from authdrf.web.serializers.user_serializers import PasswordSerializer
from tests.base_tests import UserTestData


class TestPasswordSerializer(TestCase):
    def test_raises_validation_error_if_passwords_do_not_match(self) -> None:
        test_password = UserTestData()._generate_password()
        test_data = {"password": test_password, "confirm_password": "wrong"}
        serializer = PasswordSerializer(data=test_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
