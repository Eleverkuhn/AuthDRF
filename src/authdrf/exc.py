from typing import override


class CustomValueError(ValueError):
    default_message: str

    @override
    def __init__(self) -> None:
        super().__init__(self.default_message)


class AuthenticationError(CustomValueError):
    pass


class JWTError(CustomValueError):
    pass


class EmailNotFound(AuthenticationError):
    default_message = "Invalid email"


class InvalidPassword(AuthenticationError):
    default_message = "Invalid password"


class InvalidToken(JWTError):
    default_message = "Invalid token"


class ExpiredToken(JWTError):
    default_message = "Token expired"


class InvalidSignature(JWTError):
    default_message = "Invalid token signature"
