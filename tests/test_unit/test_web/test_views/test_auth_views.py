from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from authdrf.web.views.auth_views import SignUpView
from authdrf.data.models.user_models import User
from tests.base_tests import BaseUserTest, BaseViewTestMixin


class TestSignUpView(BaseUserTest, BaseViewTestMixin, TestCase):
    url = reverse("sign_up")
    template = SignUpView.template_name

    def test_correct_template_is_used(self) -> None:
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "sign_up.xhtml")

    def test_creates_new_user(self) -> None:
        self.client.post(self.url, data=self.request_data)
        created_user = User.objects.get(email=self.request_data["email"])
        self.assertTrue(created_user)

    def test_redirects_to_main_page_on_succeed(self) -> None:
        response = self.client.post(
            self.url, data=self.request_data, follow=False
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("main"))

    def test_main_page_contains_succeed_message_after_redirection(self) -> None:
        response = self.client.post(self.url, self.request_data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Your account has been successfully created",
            response.content.decode()
        )
