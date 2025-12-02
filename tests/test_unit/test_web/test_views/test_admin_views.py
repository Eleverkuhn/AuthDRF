from typing import override

from django.urls import reverse
from django.test import TestCase

from logger.setup import LoggingConfig
from authdrf.web.views.admin_views import (
    AdminDashboardUsersView,
    AdminDashboardPermissionsView,
    AdminDashboardRolesView
)
from authdrf.data.models.user_models import User, UserRepository
from authdrf.data.models.permission_models import (
    RoleRepository, Permission, Role
)
from tests.base_tests import (
    TestAdminViewMixin, UserTestData, APIClientAdminTest
)


class BaseAdminUsersTest(TestCase):
    url = reverse("admin_users")


class BaseAdminRolesTest(TestCase):
    url = reverse("admin_roles")


class TestAdminDashboardPermissionsView(TestAdminViewMixin, TestCase):
    url = reverse("admin_permissions")
    template = AdminDashboardPermissionsView.template_name

    def test_all_permissions_are_displayed(self) -> None:
        permissions = Permission.objects.all()
        response = self.client.get(self.url)
        content = response.content.decode()

        for permission in permissions:
            self.assertIn(permission.title, content)

    def test_creates_new_permission(self) -> None:
        request_data = {"permission": "can_add_permission"}
        response = self.client.post(self.url, data=request_data)
        self.assertIn(request_data["permission"], response.content.decode())

    def test_deletes_permission(self) -> None:
        permission_to_delete = Permission.objects.get(id=1)
        response = self.client.get(self.url)

        self.assertIn(permission_to_delete.title, response.content.decode())

        request_data = {"permission": permission_to_delete}
        response = self.client.delete(self.url, data=request_data)

        self.assertNotIn(permission_to_delete.title, response.content.decode())


class TestAdminDashboardRolesView(TestAdminViewMixin, BaseAdminRolesTest):
    template = AdminDashboardRolesView.template_name

    def test_all_roles_are_displayed(self) -> None:
        roles, content = self._prepare_test_data()
        for role in roles:
            self.assertIn(role.title, content)

    def test_all_permissions_for_specific_role_are_displayed(self) -> None:
        roles, content = self._prepare_test_data()
        for role in roles:
            for permission in role.permissions.all():
                self.assertIn(permission.title, content)

    def test_deletes_role(self) -> None:
        role = Role.objects.get(id=1)
        response = self.client.get(self.url)
        self.assertIn(role.title, response.content.decode())

        request_data = {"role": role.id}
        response = self.client.delete(self.url, data=request_data)
        self.assertNotIn(role.title, response)

    def _prepare_test_data(self) -> tuple:
        roles = Role.objects.all()
        response = self.client.get(self.url)
        content = response.content.decode()
        return (roles, content)


class TestAdminDashboardRolesPATCHView(APIClientAdminTest, BaseAdminRolesTest):
    def test_patch_adds_permission_for_a_role(self) -> None:
        permission = Permission.objects.get(id=5)
        role = Role.objects.get(id=1)
        self.assertNotIn(permission, role.permissions.all())
        update_data = {"permission_id": permission.id, "role": role.id}

        self.client.patch(self.url, data=update_data)
        updated_role = Role.objects.get(id=role.id)
        self.assertIn(permission, updated_role.permissions.all())


class TestAdminDashboardView(TestAdminViewMixin, BaseAdminUsersTest):
    template = AdminDashboardUsersView.template_name

    def test_all_active_users_are_displayed(self) -> None:
        users = UserRepository.active_users()
        response = self.client.get(self.url)
        content = response.content.decode()

        for user in users:
            self.assertIn(str(user.id), content)
            self.assertIn(user.email, content)
            self.assertIn(str(user.role), content)


class TestAdminDashboardUsersPATCH(APIClientAdminTest, BaseAdminUsersTest):
    def test_patch_updates_user_role(self) -> None:
        test_user = UserTestData().create_user()
        subscriber_id = RoleRepository().subscriber.id
        update_data = {"user_id": test_user.id, "role": subscriber_id}

        response = self.client.patch(self.url, data=update_data)
        LoggingConfig().logger.debug(response)

        user_db = User.objects.get(id=test_user.id)
        self.assertEqual(user_db.role.id, subscriber_id)
