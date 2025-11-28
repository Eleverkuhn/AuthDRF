from logger.setup import LoggingConfig
from authdrf.web.serializers.user_serializers import UserSerializer
from authdrf.data.models.user_models import User


class SignUpService:
    def __init__(self, request_data: dict) -> None:
        self.request_data = request_data

    def exec(self) -> None:
        validated_data = self.validate_request_data()
        User.objects.create_user(**validated_data)

    def validate_request_data(self) -> dict:
        LoggingConfig().logger.debug(self.request_data)
        serializer = UserSerializer(data=self.request_data)
        if serializer.is_valid(raise_exception=True):
            return serializer.validated_data
