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
