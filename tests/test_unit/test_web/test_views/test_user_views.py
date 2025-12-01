from django.urls import reverse
from django.test import TestCase

from authdrf.web.views.user_views import UserPageView
from tests.base_tests import BaseTestProtectedViewMixin


class TestUserPageView(BaseTestProtectedViewMixin, TestCase):
    url = reverse("user_page")
    template = UserPageView.template_name
