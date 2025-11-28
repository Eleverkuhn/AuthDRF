import requests

import psycopg
from django.test import TestCase
from django.db import connection, connections
from django.db.utils import OperationalError

from config.settings.dev import env
from logger.setup import LoggingConfig


class BaseDatabaseTest:
    def execute_test_query(self, cursor: psycopg.Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class TestProjectSetup(TestCase, BaseDatabaseTest):
    def test_env_variables_loaded(self) -> None:
        self.assertTrue(env.postgres_password)
        self.assertTrue(env.postgres_user)
        self.assertTrue(env.postgres_db)
        self.assertTrue(env.postgres_port)
        self.assertTrue(env.postgres_host)

    def test_connection_to_postgres(self) -> None:
        conn_params = {
            "dbname": env.postgres_db,
            "user": env.postgres_user,
            "password": env.postgres_password,
            "host": env.postgres_host,
            "port": env.postgres_port
        }
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                self.execute_test_query(cursor)

    def test_connection_to_django_container(self) -> None:
        url = f"http://{env.django_container_host}:8000/"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException as exc:
            self.fail(f"Django server not reachable: {exc}")

    def test_django_connected_to_posgtgres(self) -> None:
        try:
            connections['default'].cursor()
        except OperationalError:
            self.fail("Database connection failed!")
        else:
            cursor = connection.cursor()
            self.execute_test_query(cursor)


class TestLoggingConfig(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.logger_config = LoggingConfig()
        cls.test_log_message = "test"

    def test_logger_config_file_is_loaded(self) -> None:
        config = self.logger_config.load()
        self.assertTrue(config)

    def test_logger_outputs_debug_messages_to_console(self) -> None:
        with self.assertLogs(self.logger_config.logger, level="DEBUG") as cm:
            self.logger_config.logger.debug(self.test_log_message)
        self.assertTrue(any(self.test_log_message in msg for msg in cm.output))
