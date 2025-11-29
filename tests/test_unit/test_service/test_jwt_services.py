import time
from unittest import TestCase

from logger.setup import LoggingConfig
from authdrf.exc import InvalidToken, ExpiredToken, InvalidSignature
from authdrf.service.jwt_services import (
    JWTEncodingService, JWTDecodingService, JWTValidator, JWT
)


class BaseJWTServiceTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_payload = {"id": 1}


class TestJWTEncodingService(BaseJWTServiceTest):
    def test_exec_creates_jwt(self) -> None:
        token = JWTEncodingService(self.test_payload).exec()
        token_parts = token.split(".")
        self.assertEqual(len(token_parts), 3)


class TestJWTDecodingService(BaseJWTServiceTest):
    def test_exec_decodes_token_and_payload_matches(self) -> None:
        token = JWTEncodingService(self.test_payload).exec()
        payload = JWTDecodingService(token).exec()
        self.assertEqual(payload, self.test_payload)

    def test_raises_invalid_token_exc_if_wrong_token_type(self) -> None:
        invalid_token = 2130194
        with self.assertRaises(InvalidToken):
            JWTDecodingService._validate_type(invalid_token)

    def test_raises_expired_token_exc(self) -> None:
        token = JWTEncodingService(self.test_payload, 1).exec()
        time.sleep(2)
        with self.assertRaises(ExpiredToken):
            JWTDecodingService(token).exec()

    def test_raises_invalid_signature_exc_if_signatures_do_not_match(self) -> None:
        token = JWTEncodingService(self.test_payload).exec()
        splitted_token = token.split(".")
        splitted_token[0] = "invalid_token"
        modified_token = JWT(*splitted_token)
        with self.assertRaises(InvalidSignature):
            JWTDecodingService(modified_token.value).exec()


class TestJWTValidator(TestCase):
    def setUp(self) -> None:
        self.invalid_tokens = {
            "len_lt_3": "2324234".split("."),
            "len_ht_3": "in.vali.d.token".split("."),
            "empty_string": "in.valid.".split(".")
        }

    def test_raises_invalid_token_exc(self) -> None:
        for token in self.invalid_tokens.values():
            with self.assertRaises(InvalidToken):
                JWTValidator(token).validate()
