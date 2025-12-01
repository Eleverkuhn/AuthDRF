from typing import override

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from authdrf.web.views.base_views import BaseViewMixin, ProtectedViewMixin
from authdrf.web.serializers.user_serializers import (
    PersonalUserSerializer, PasswordSerializer
)


class UserPageView(ProtectedViewMixin, BaseViewMixin, APIView):
    template_name = "my.xhtml"
    serializer_class = PersonalUserSerializer

    @override
    def get(self, request: Request) -> Response:
        content = {
            "personal_serializer": PersonalUserSerializer(request.user),
            "password_serializer": PasswordSerializer()
        }
        response = Response(content, status=status.HTTP_200_OK)
        return response
