from django.core.management.base import BaseCommand

from authdrf.data.models.user_models import UserRepository
from tests.base_tests import UserTestData


class Command(BaseCommand):
    help = "Create an admin user interactively"

    def handle(self, *args, **options):
        email = input("Enter email: ")
        password = input("Enter password: ")
        admin_data = {
            **UserTestData()._generate_personal_user_data(),
            "email": email,
            "password": password
        }
        UserRepository(admin_data).create_admin()
        self.stdout.write(self.style.SUCCESS(f"Admin {email} created successfully"))
