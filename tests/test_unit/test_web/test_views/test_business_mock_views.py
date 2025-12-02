from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.response import Response

from authdrf.exc import PermissionError
from authdrf.service.auth_services import TokenService
from authdrf.web.views.business_mock_views import (
    PublicPostMockView,
    SubscriberPostMockView,
    PremiumPostMockView
)
from tests.base_tests import (
    UserTestData,
    BaseViewTestMixin,
    BaseTestProtectedViewMixin,
    TestSubscriberViewMixin,
    TestPremiumSubscriberViewMixin
)


class TestPublicPostMockView(BaseTestProtectedViewMixin, BaseViewTestMixin, TestCase):
    url = reverse("public_post", kwargs={"id": 1})
    template = PublicPostMockView.template_name


class TestSubscriberPostMockView(TestSubscriberViewMixin, TestCase):
    url = reverse("subscriber_post", kwargs={"id": 1})
    template = SubscriberPostMockView.template_name

    def test_authoirzed_user_with_no_permissions_can_not_get_access(self) -> None:
        guest = UserTestData().create_user()
        response = Response()
        client = Client()
        access_token = TokenService(response, guest.id).access_token
        client.cookies["access_token"] = access_token
        client.cookies["refresh_token"] = access_token

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(PermissionError.default_message, response.content.decode())


class TestPremiumPostMockView(TestPremiumSubscriberViewMixin, TestCase):
    url = reverse("premium_post", kwargs={"id": 1})
    template = PremiumPostMockView.template_name
