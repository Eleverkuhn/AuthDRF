from authdrf.data.models.user_models import User


class SignUpService:
    def __init__(self, user_data: dict) -> None:
        self.user_data = user_data

    def exec(self) -> None:
        self.user_data.pop("confirm_password")
        User.objects.create_user(**self.user_data)

    @staticmethod
    def success_message() -> str:
        return "Your account has been successfully created"
