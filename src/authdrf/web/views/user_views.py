from typing import override

from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from logger.setup import LoggingConfig
from authdrf.exc import UserAlreadyExists
from authdrf.web.views.base_views import (
    BaseViewMixin, ProtectedViewMixin, RedirectResponse
)
from authdrf.web.serializers.user_serializers import (
    PersonalUserSerializer, PasswordSerializer
)
from authdrf.service.user_services import UserService
from authdrf.data.models.user_models import User


class UserPageView(ProtectedViewMixin, BaseViewMixin, APIView):
    template_name = "my.xhtml"
    serializer_class = PersonalUserSerializer

    @override
    def get(self, request: Request) -> Response:
        response = self._construct_response(request.user)
        return response

    def post(self, request: Request) -> Response | RedirectResponse:
        if request.POST.get("_method") == "PUT":
            return self.put(request)

    def put(self, request: Request) -> Response | RedirectResponse:
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"serializer": serializer})
        else:
            response = self.update_personal_info(request, serializer)
            return response

    def update_personal_info(
            self, request: Request, serializer: PersonalUserSerializer
    ) -> Response | RedirectResponse:
        try:
            user = UserService(serializer.validated_data).update(request.user.id)
        except UserAlreadyExists as error:
            return Response(
                {"serializer": self.serializer_class(request.user), "error": str(error)}
            )
        else:
            response = self._construct_response(user)
            return response

    def _construct_response(self, user: User) -> Response:
        content = {"serializer": self.serializer_class(user)}
        response = Response(content, status=status.HTTP_200_OK)
        return response
