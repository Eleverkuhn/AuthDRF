from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from authdrf.data.models.user_models import User
from tests.base_tests import BaseUserTest


class TestSignUpView(BaseUserTest, TestCase):
    def test_get_returns_200_OK(self) -> None:
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_template_is_used(self) -> None:
        response = self.client.get(reverse("sign_up"))
        self.assertTemplateUsed(response, "sign_up.xhtml")

    def test_creates_new_user(self) -> None:
        self.client.post(reverse("sign_up"), data=self.request_data)
        created_user = User.objects.get(email=self.request_data["email"])
        self.assertTrue(created_user)
