from django.test import TestCase
from django.urls import reverse

from authdrf.web.views.main_views import MainView
from tests.base_tests import BaseViewTestMixin


class TestMainView(BaseViewTestMixin, TestCase):
    url = reverse("main")
    template = MainView.template_name
