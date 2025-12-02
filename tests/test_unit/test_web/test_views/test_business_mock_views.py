from django.urls import reverse
from django.test import TestCase

from authdrf.web.views.business_mock_views import PublicPostMockView
from tests.base_tests import BaseViewTestMixin, BaseTestProtectedViewMixin


class TestPublicPostMockView(BaseTestProtectedViewMixin, BaseViewTestMixin, TestCase):
    url = reverse("public_post", kwargs={"id": 1})
    template = PublicPostMockView.template_name
