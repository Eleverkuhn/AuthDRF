from django.urls import reverse
from django.test import TestCase

from logger.setup import LoggingConfig
from authdrf.web.views.admin_views import AdminDashboardUsersView
from authdrf.data.models.user_models import User, UserRepository
from authdrf.data.models.permission_models import RoleRepository
from tests.base_tests import (
    TestAdminViewMixin, UserTestData, APIClientAdminTest
)


class BaseAdminTest(TestCase):
    url = reverse("admin_users")


class TestAdminDashboardView(TestAdminViewMixin, BaseAdminTest):
    template = AdminDashboardUsersView.template_name

    def test_all_active_users_are_displayed(self) -> None:
        users = UserRepository.active_users()
        response = self.client.get(self.url)
        content = response.content.decode()
        for user in users:
            self.assertIn(str(user.id), content)
            self.assertIn(user.email, content)
            self.assertIn(str(user.role), content)


class TestAdminDashboardUsersPATCH(APIClientAdminTest, BaseAdminTest):
    def test_patch_updates_user_role(self) -> None:
        test_user = UserTestData().create_user()
        subscriber_id = RoleRepository().subscriber.id
        update_data = {"user_id": test_user.id, "role": subscriber_id}

        response = self.client.patch(self.url, data=update_data)
        LoggingConfig().logger.debug(response)

        user_db = User.objects.get(id=test_user.id)
        self.assertEqual(user_db.role.id, subscriber_id)
