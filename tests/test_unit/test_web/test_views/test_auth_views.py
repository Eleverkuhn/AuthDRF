from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class TestSignUpView(TestCase):
    def test_get_returns_200_OK(self) -> None:
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_template_is_used(self) -> None:
        response = self.client.get(reverse("sign_up"))
        self.assertTemplateUsed(response, "sign_up.xhtml")
