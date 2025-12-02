from django.urls import reverse
from django.test import TestCase

from authdrf.web.views.admin_views import AdminDashboardView
from tests.base_tests import TestAdminViewMixin


class TestAdminDashboardView(TestAdminViewMixin, TestCase):
    url = reverse("admin")
    template = AdminDashboardView.template_name
