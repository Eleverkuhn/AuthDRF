import base64
import hashlib
import hmac
import json
import time
from typing import Any

from config.settings.dev import env

type Payload = dict[str, Any]
type TokenPart = dict[str, str] | Payload


class JWTService:
    pass


class JWTEncodingService:
    header = {"alg": "H256", "type": "JWT"}

    def __init__(self, payload: Payload, exp_seconds: int = 600) -> None:
        self.payload = payload
        self.exp_seconds = exp_seconds

    @staticmethod
    def current_time() -> int:
        return int(time.time())

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

    def encode(self) -> bytes:
        token_part_bytes = json.dumps(self.token_part).encode()
        token_part_b64 = self._encode_to_b64(token_part_bytes)
        return token_part_b64

    @classmethod
    def _encode_to_b64(cls, token_part: bytes) -> bytes:
        token_part_b64 = base64.urlsafe_b64encode(token_part).rstrip(b"=")
        return token_part_b64
