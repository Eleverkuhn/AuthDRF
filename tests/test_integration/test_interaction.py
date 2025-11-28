from typing import override

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from logger.setup import LoggingConfig
from config.settings.dev import env


class BaseInteractionTest(LiveServerTestCase):
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768

    def setUp(self) -> None:
        options = Options()
        options.add_argument(f"--width={self.WINDOW_WIDTH}")
        options.add_argument(f"--height={self.WINDOW_HEIGHT}")
        options.add_argument("--headless")
        self.browser = webdriver.Remote(
            command_executor=f"http://{env.selenium_host}:{env.selenium_port}/wd/hub",
            options=options
        )
        self.base_url = f"http://{env.live_server}:{env.django_port}/"


class TestSignUpWorkflow(BaseInteractionTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = "".join([self.base_url, "auth/sign-up/"])
        self.field_to_placeholder = {
            "first-name": "John",
            "middle-name": "Michael",
            "last-name": "Doe",
            "email": "email@example.com"
        }

    def tearDown(self) -> None:
        self.browser.quit()

    def test(self) -> None:
        # User opens 'sign-up' page
        self.browser.get(self.url)
        self.browser.set_window_size(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # User sees 'sign-up' form
        self.browser.find_element(By.ID, "sign-up-form")

        # 'Sign up' form contains 'first name', 'middle name', 'last name '
        # 'email', 'password' and 'confirm_password' fields, their
        # placeholders and 'Sign Up' button
        self._check_fields_with_placeholders()
        self.browser.find_element(By.ID, "password")
        self.browser.find_element(By.ID, "confirm-password")
        self.browser.find_element(By.ID, "sign-up-button")

    def _check_fields_with_placeholders(self) -> None:
        for field_id, expected_placeholder in self.field_to_placeholder.items():
            field = self.browser.find_element(By.ID, field_id)
            placeholder_text = field.get_attribute("placeholder")
            self.assertEqual(placeholder_text, expected_placeholder)
