from django.urls import reverse
from django.test import TestCase, Client

from authdrf.exc import AuthorizationError
from authdrf.web.views.user_views import UserPageView
from tests.base_tests import BaseTestProtectedViewMixin


class TestUserPageView(BaseTestProtectedViewMixin, TestCase):
    url = reverse("user_page")
    template = UserPageView.template_name

    def test_unlogged_in_user_can_not_view_content(self) -> None:
        response = Client().get(self.url)
        self.assertIn(
            AuthorizationError.default_message,
            response.content.decode()
        )
