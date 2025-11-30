from authdrf.exc import EmailNotFound
from authdrf.data.models.user_models import User, UserRepository


class BaseService:
    def __init__(self, request_data: dict) -> None:
        self.request_data = request_data


class SignUpService(BaseService):
    def exec(self) -> None:
        self.request_data.pop("confirm_password")
        UserRepository(self.request_data).create()

    @staticmethod
    def success_message() -> str:
        return "Your account has been successfully created"


class SignInService(BaseService):
    def exec(self) -> None:
        self.check_user_exists()

    def check_user_exists(self) -> None:
        try:
            user = User.objects.get(email=self.request_data["email"])
        except User.DoesNotExist:
            raise EmailNotFound()
        else:
            return user
