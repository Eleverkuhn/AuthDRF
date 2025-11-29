from faker import Faker


class BaseUserTest:  # TODO: rename to 'BaseAuthTest'
    def setUp(self) -> None:
        super().setUp()
        self.request_data = UserTestData().generate()


class UserTestData:
    def __init__(self) -> None:
        self.faker = Faker()

    def generate(self) -> dict[str, str]:
        test_password = self._generate_password()
        test_data = {
            "first_name": self.faker.first_name(),
            "middle_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": self.faker.email(),
            "password": test_password,
            "confirm_password": test_password
        }
        return test_data

    def _generate_password(self) -> str:
        test_password = self.faker.password(
            length=10,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True
        )
        return test_password


class BaseAuthTest:  # TODO: Move setUp to 'SignUpWorkflow' and remove this class
    def setUp(self) -> None:
        super().setUp()
        self.test_pasword = "C0mplic@tedTeStpass"
        self.field_to_placeholder = {
            "first-name": "John",
            "middle-name": "Michael",
            "last-name": "Doe",
            "email": "email@example.com"
        }
        self.sign_up_data = {
            **self.field_to_placeholder,
            "password": self.test_pasword,
            "confirm-password": self.test_pasword,
        }
