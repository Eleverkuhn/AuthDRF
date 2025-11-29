from typing import override


class JWTError(ValueError):
    default_message: str

    @override
    def __init__(self) -> None:
        super().__init__(self.default_message)


class InvalidToken(JWTError):
    default_message = "Invalid token"


class ExpiredToken(JWTError):
    default_message = "Token expired"


class InvalidSignature(JWTError):
    default_message = "Invalid token signature"
