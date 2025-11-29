from unittest import TestCase

from authdrf.service.jwt_services import JWTEncodingService


class TestJWTEncodingService(TestCase):
    def test_encode_creates_jwt(self) -> None:
        test_payload = {"id": 1}
        jwt_token = JWTEncodingService(test_payload).exec()
        jwt_token_parts = jwt_token.split(".")
        self.assertEqual(len(jwt_token_parts), 3)
