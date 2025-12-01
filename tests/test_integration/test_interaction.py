from typing import override

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from config.settings.dev import env
from authdrf.web.serializers.user_serializers import (
    UserSerializer, SignInSerializer
)
from tests.base_tests import UserTestData


class BaseInteractionTest(StaticLiveServerTestCase):
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768

    def setUp(self) -> None:
        super().setUp()
        options = Options()
        options.add_argument(f"--width={self.WINDOW_WIDTH}")
        options.add_argument(f"--height={self.WINDOW_HEIGHT}")
        options.add_argument("--headless")
        self.browser = webdriver.Remote(
            command_executor=f"http://{env.selenium_host}:{env.selenium_port}/wd/hub",
            options=options
        )
        self.base_url = f"http://{env.live_server}:{env.django_port}"

    def tearDown(self) -> None:
        try:
            self.browser.quit()
        finally:
            super().tearDown()

    def open_page(self) -> None:
        self.browser.get(self.url)
        self.browser.set_window_size(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def form_rendering(self) -> None:
        for serializer_field in self.serializer:
            field = self.browser.find_element(By.ID, serializer_field.name)
            self.assertEqual(
                field.get_attribute("placeholder"),
                serializer_field.help_text
            )

    def fill_in_form(self, data: dict) -> None:
        for field_name, submit_value in data.items():
            input_box = self.browser.find_element(By.NAME, field_name)
            input_box.send_keys(submit_value)


class BaseWorkflowWithCreatedUser(BaseInteractionTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.sign_up_data = UserTestData().generate_sign_up_data()
        self._create_user()

    def _create_user(self) -> None:
        self.browser.get("".join([self.base_url, reverse("sign_up")]))
        self.fill_in_form(self.sign_up_data)
        self.browser.find_element(By.ID, "sign-up-button").click()


class TestSignUpWorkflow(BaseInteractionTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = "".join([self.base_url, reverse("sign_up")])
        self.request_data = UserTestData().generate_sign_up_data()
        self.serializer = UserSerializer()

    def test(self) -> None:
        # User opens 'sign-up' page
        self.open_page()

        # User sees 'sign-up' form
        self.browser.find_element(By.ID, "sign-up-form")

        # 'Sign up' form contains 'first name', 'middle name', 'last name '
        # 'email', 'password' and 'confirm_password' fields, their
        # placeholders and 'Sign Up' button
        self.form_rendering()
        self.browser.find_element(By.ID, "sign-up-button")

        # User fill in the fields and submit the form
        self.fill_in_form(self.request_data)
        self.browser.find_element(By.ID, "sign-up-button").click()

        # User get redirected to the main page
        main_page = "".join([self.base_url, reverse("main")])
        self.assertEqual(self.browser.current_url, main_page)


class TestSignInWorkflow(BaseWorkflowWithCreatedUser):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = "".join([self.base_url, reverse("sign_in")])
        self.serializer = SignInSerializer()
        self.request_data = {
            "email": self.sign_up_data["email"],
            "password": self.sign_up_data["password"]
        }

    def test(self) -> None:
        # User opens 'sign-in' page
        self.open_page()

        # User sees `sign-in` form
        self.browser.find_element(By.ID, "sign-in-form")

        # 'Sign in' form contains 'email', 'password' fields and 'Sgin In'
        # button. 'Email' field have a placeholder
        self.form_rendering()
        self.browser.find_element(By.ID, "sign-in-button")

        # User fill in the fields and submit the form
        self.fill_in_form(self.request_data)
        self.browser.find_element(By.ID, "sign-in-button").click()

        # User get redirected to his personal page
        user_page = "".join([self.base_url, reverse("user_page")])
        self.assertEqual(self.browser.current_url, user_page)
