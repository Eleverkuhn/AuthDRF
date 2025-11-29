import base64
import hashlib
import hmac
import json
import time
from typing import Any

from config.settings.dev import env
from authdrf.exc import InvalidToken, ExpiredToken, InvalidSignature

type Payload = dict[str, Any]
type TokenPart = dict[str, str] | Payload


class BaseJWTEncodingService:
    @staticmethod
    def current_time() -> int:
        return int(time.time())


class JWTDecodingService(BaseJWTEncodingService):
    def __init__(self, token: str) -> None:
        self.token = token
        self.jwt = self.set_jwt(self.token)

    def set_jwt(self, token: str) -> "JWT":
        token_parts = self._validate_type(token)
        JWTValidator(token_parts).validate()
        return JWT(*token_parts)

    @staticmethod
    def _validate_type(token: str) -> list[str]:
        try:
            token_parts = token.split(".")
        except Exception:
            raise InvalidToken()
        else:
            return token_parts

    def exec(self) -> Payload:
        self._compare_signatures()
        payload = self._get_payload()
        self._check_exp_time(payload)
        return payload

    def _compare_signatures(self) -> None:
        signature, valid_signature = self._construct_signatures()
        JWTSignatureService.compare(signature, valid_signature)

    def _construct_signatures(self) -> tuple[bytes, bytes]:
        signature = JWTSignatureService(
            self.jwt.header.encode(), self.jwt.payload.encode()
        ).construct_signature()
        valid_signature = B64EncodingService.decode(self.jwt.signature)
        return (signature, valid_signature)

    def _get_payload(self) -> Payload:
        payload_b64 = B64EncodingService.decode(self.jwt.payload)
        payload = json.loads(payload_b64)
        return payload

    def _check_exp_time(self, payload: Payload) -> None:
        if payload["exp"] < self.current_time():
            raise ExpiredToken()


class JWTValidator:
    def __init__(self, token_parts: list[str]) -> None:
        self.token_parts = token_parts

    @property
    def check_structure_is_valid(self) -> bool:
        return len(self.token_parts) == 3

    @property
    def check_part_is_empty(self) -> bool:
        return any(part == "" for part in self.token_parts)

    def validate(self) -> None:
        if not self.check_structure_is_valid:
            raise InvalidToken()
        if self.check_part_is_empty:
            raise InvalidToken()


class JWTEncodingService(BaseJWTEncodingService):
    header = {"alg": "H256", "type": "JWT"}

    def __init__(self, payload: Payload, exp_seconds: int = 600) -> None:
        self.payload = payload
        self.exp_seconds = exp_seconds

    @property
    def exp_time(self) -> int:
        return self.current_time() + self.exp_seconds

    def exec(self) -> str:
        jwt_parts = self._construct_jwt()
        jwt = b".".join(jwt_parts).decode()
        return jwt

    def _construct_jwt(self) -> tuple[bytes, bytes, bytes]:
        header = B64EncodingService(self.header).encode()
        payload = self._construct_payload()
        signature = JWTSignatureService(header, payload).create()
        return (header, payload, signature)

    def _construct_payload(self) -> bytes:
        self.payload.update({"exp": self.exp_time})
        payload = B64EncodingService(self.payload).encode()
        return payload


class JWTSignatureService:
    def __init__(self, header: bytes, payload: bytes) -> None:
        self.header = header
        self.payload = payload

    @property
    def input(self) -> bytes:
        return b".".join([self.header, self.payload])

    @property
    def key(self) -> bytes:
        return env.django_key.encode()

    @classmethod
    def compare(cls, signature: bytes, expected_signature: bytes) -> None:
        if not hmac.compare_digest(signature, expected_signature):
            raise InvalidSignature()

    def create(self) -> bytes:
        signature = self.construct_signature()
        signature_b64 = B64EncodingService._encode_to_b64(signature)
        return signature_b64

    def construct_signature(self) -> bytes:
        signature = hmac.new(
            key=self.key, msg=self.input, digestmod=hashlib.sha256
        ).digest()
        return signature


class B64EncodingService:
    def __init__(self, token_part: TokenPart) -> None:
        self.token_part = token_part

    @classmethod
    def decode(cls, token_part: str) -> bytes:
        padded = token_part + "=" * (-len(token_part) % 4)
        return base64.urlsafe_b64decode(padded)

    def encode(self) -> bytes:
        token_part_bytes = json.dumps(self.token_part).encode()
        token_part_b64 = self._encode_to_b64(token_part_bytes)
        return token_part_b64

    @classmethod
    def _encode_to_b64(cls, token_part: bytes) -> bytes:
        token_part_b64 = base64.urlsafe_b64encode(token_part).rstrip(b"=")
        return token_part_b64


class JWT:
    def __init__(self, header: str, payload: str, signature: str) -> None:
        self.header = header
        self.payload = payload
        self.signature = signature

    @property
    def value(self) -> str:
        return ".".join([self.header, self.payload, self.signature])
