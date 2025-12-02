from typing import override


class CustomValueError(ValueError):
    default_message: str

    @override
    def __init__(self) -> None:
        super().__init__(self.default_message)


class UserAlreadyExists(CustomValueError):
    default_message = "User with this email already exists"


class AuthenticationError(CustomValueError):
    pass


class PermissionError(CustomValueError):
    default_message = "You do not have rights to view this page"


class AuthorizationError(CustomValueError):
    default_message = "You need to sign in to view content of this page"


class RefreshRequired(AuthorizationError):
    default_message = "Refresh access token"


class JWTError(CustomValueError):
    pass


class EmailNotFound(AuthenticationError):
    default_message = "Invalid email"


class UserDoesNotExist(AuthenticationError):
    default_message = "User does not exist"


class InvalidPassword(AuthenticationError):
    default_message = "Invalid password"


class InvalidToken(JWTError):
    default_message = "Invalid token"


class ExpiredToken(JWTError):
    default_message = "Token expired"


class InvalidSignature(JWTError):
    default_message = "Invalid token signature"
