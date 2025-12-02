from django.db import models

from authdrf.data.models.base_models import ModelFieldDefault


class Permission(models.Model):
    title = models.CharField(
        unique=True, max_length=ModelFieldDefault.TITLE_LENGTH
    )


class Role(models.Model):
    title = models.CharField(
        unique=True, max_length=ModelFieldDefault.TITLE_LENGTH
    )
    description = models.TextField()

    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return self.title


class RoleRepository:
    @property
    def subscriber_permissions(self) -> list[str]:
        return self.subscriber.permissions.all()

    @property
    def subscriber(self) -> Role:
        return Role.objects.get(id=1)

    @property
    def premium_subscriber_permissions(self) -> list[str]:
        return self.premium_subscriber.permissions.all()

    @property
    def premium_subscriber(self) -> Role:
        return Role.objects.get(id=2)

    @property
    def admin_permissions(self) -> list[str]:
        return self.admin.permissions.all()

    @property
    def admin(self) -> Role:
        return Role.objects.get(id=3)
