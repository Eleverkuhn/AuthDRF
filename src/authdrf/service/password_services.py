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
        return bcrypt.checkpw(
            self.password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )

    def hash(self) -> bytes:
        hashed_password = bcrypt.hashpw(
            self.password.encode("utf-8"), bcrypt.gensalt()
        )
        return hashed_password.decode("utf-8")

    def verify(self) -> None:
        if not self.check_hash_matches:
            raise InvalidPassword()
