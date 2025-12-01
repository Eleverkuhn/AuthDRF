from django.urls import reverse
from django.test import TestCase

from logger.setup import LoggingConfig
from authdrf.web.views.user_views import UserPageView
from authdrf.web.serializers.user_serializers import PersonalUserSerializer
from tests.base_tests import BaseTestProtectedViewMixin


class TestUserPageView(BaseTestProtectedViewMixin, TestCase):
    url = reverse("user_page")
    template = UserPageView.template_name

    def test_contains_user_info(self) -> None:
        personal_info = PersonalUserSerializer(self.user).data
        response = self.client.get(self.url)
        for value in personal_info.values():
            self.assertIn(value, response.content.decode())
