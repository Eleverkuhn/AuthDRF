from django.test import TestCase

from authdrf.service.admin_services import AdminDashboardService
from authdrf.data.models.user_models import User
from authdrf.data.models.permission_models import RoleRepository
from tests.base_tests import TestWithCreatedSubscriberMixin


class TestAdminDashboardService(TestWithCreatedSubscriberMixin, TestCase):
    def test_changes_user_role(self) -> None:
        old_role = self.user.role
        role_id = RoleRepository().premium_subscriber.id
        request_data = {"user_id": self.user.id, "role": role_id}

        AdminDashboardService(request_data).change_user_role()
        user_db = User.objects.get(id=self.user.id)

        self.assertNotEqual(old_role.id, user_db.role.id)
