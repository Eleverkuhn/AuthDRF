from django.db.utils import IntegrityError

from authdrf.exc import UserAlreadyExists
from authdrf.web.serializers.user_serializers import PersonalUserSerializer
from authdrf.service.base_services import BaseService
from authdrf.data.models.user_models import User, UserRepository


class UserService(BaseService):
    def update(self, user_id: int) -> User:
        user = User.objects.get(id=user_id)
        update_data = self.construct_update_data(user)
        self.update_user(user, update_data)
        return user

    def construct_update_data(self, user: User) -> dict:
        user_data = PersonalUserSerializer(user).data
        update_data = {
            field: value
            for field, value
            in self.request_data.items()
            if user_data.get(field) != value
        }
        return update_data

    def update_user(self, user: User, update_data: dict) -> None:
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
            user.save()
        except IntegrityError:
            raise UserAlreadyExists()

    def change_password(self, user_id: int) -> None:
        self.request_data.pop("confirm_password")
        UserRepository(self.request_data).change_password(user_id)

    @staticmethod
    def delete(user_id: int) -> None:
        UserRepository.set_is_active_to_false(user_id)
