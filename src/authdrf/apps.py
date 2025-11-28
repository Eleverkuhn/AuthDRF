from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authdrf'

    def ready(self) -> None:
        from .data.models import user_models
