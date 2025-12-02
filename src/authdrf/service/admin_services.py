from django.db.models.query import QuerySet

from authdrf.service.base_services import BaseService
from authdrf.data.models.user_models import User, UserRepository
from authdrf.data.models.permission_models import Role, Permission


class AdminDashboardService(BaseService):
    def add_permission(self) -> None:
        Permission(title=self.request_data["permission"]).save()

    def delete_permission(self) -> None:
        permission = self.get_permission()
        permission.delete()

    def get_permission(self) -> Permission:
        return Permission.objects.get(id=self.request_data["permission_id"])

    def change_user_role(self) -> None:
        user = self.get_user()
        user.role = self.get_role()
        user.save()

    def get_user(self) -> User:
        return User.objects.get(id=self.request_data["user_id"])

    def get_role(self) -> Role:
        return Role.objects.get(id=self.request_data["role"])

    @staticmethod
    def construct_permissions_content() -> dict[str, QuerySet[Permission]]:
        permissions = Permission.objects.all()
        content = {"permissions": permissions}
        return content

    @staticmethod
    def construct_users_content() -> dict[str, QuerySet[User] | QuerySet[Role]]:
        users = UserRepository.active_users()
        roles = Role.objects.all()
        content = {"users": users, "roles": roles}
        return content
