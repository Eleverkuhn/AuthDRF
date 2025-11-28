from rest_framework import serializers

from authdrf.data.models.user_models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "middle_name", "last_name"]
