import bcrypt

from authdrf.exc import InvalidPassword


class PasswordService:
    def __init__(
            self, password: str, hashed_password: bytes | None = None
    ) -> None:
        self.password = password
        self.hashed_password = hashed_password

    @property
    def check_hash_matches(self) -> bool:
        return bcrypt.checkpw(self.password.encode(), self.hashed_password)

    def hash(self) -> bytes:
        hashed_password = bcrypt.hashpw(
            self.password.encode(), bcrypt.gensalt()
        )
        return hashed_password

    def verify(self) -> None:
        if not self.check_hash_matches:
            raise InvalidPassword()
