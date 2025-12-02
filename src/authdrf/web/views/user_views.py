from typing import override

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from authdrf.exc import UserAlreadyExists
from authdrf.web.views.base_views import (
    BaseViewMixin, ProtectedViewMixin, RedirectResponse, ExtendedHTTPView
)
from authdrf.web.serializers.user_serializers import (
    PersonalUserSerializer, PasswordSerializer
)
from authdrf.service.auth_services import SignOutService
from authdrf.service.user_services import UserService
from authdrf.data.models.user_models import User


class UserPageView(ProtectedViewMixin, BaseViewMixin, ExtendedHTTPView):
    template_name = "my.xhtml"
    serializer_class = PersonalUserSerializer

    @override
    def get(self, request: Request) -> Response:
        response = self._construct_response(request.user)
        return response

    def put(self, request: Request) -> Response | RedirectResponse:
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"serializer": serializer})
        else:
            response = self.update_personal_info(request, serializer)
            return response

    def delete(self, request: Request) -> Response | RedirectResponse:
        response = redirect("main")
        UserService.delete(request.user.id)
        SignOutService(response).exec()
        return response

    def update_personal_info(
            self, request: Request, serializer: PersonalUserSerializer
    ) -> Response | RedirectResponse:
        try:
            service = UserService(serializer.validated_data)
            user = service.update(request.user.id)
        except UserAlreadyExists as error:
            content = {
                "serializer": self.serializer_class(request.user),
                "error": str(error)
            }
            return Response(content)
        else:
            response = self._construct_response(user)
            return response

    def _construct_response(self, user: User) -> Response:
        content = {"serializer": self.serializer_class(user)}
        response = Response(content, status=status.HTTP_200_OK)
        return response


class ChangePasswordView(ProtectedViewMixin, BaseViewMixin, ExtendedHTTPView):
    template_name = "change_password.xhtml"
    serializer_class = PasswordSerializer

    def put(self, request: Request) -> Response | RedirectResponse:
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"serializer": serializer})
        else:
            response = redirect("sign_in")
            service = UserService(serializer.validated_data)
            service.change_password(request.user.id)
            SignOutService(response).exec()
            return response
