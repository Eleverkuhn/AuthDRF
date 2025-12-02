from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from authdrf.exc import PermissionError
from authdrf.web.views.base_views import ProtectedViewMixin
from authdrf.service.auth_services import PermissionService
from authdrf.data.models.user_models import User
from authdrf.data.models.permission_models import Role, RoleRepository


class BaseMockView(APIView):
    def construct_content(self, post_type: str, id: int) -> dict[str, str]:
        return {"mock_object": f"Example of {post_type} level post with id {id}"}


class PermissionViewMixin:
    permissions: list[str]

    def dispatch(self, request: Request, *args, **kwargs):
        try:
            PermissionService(request.user, self.permissions).verify()
        except PermissionError as error:
            response = render(
                request,
                "response_403.xhtml",
                {"error": str(error)},
                status=status.HTTP_403_FORBIDDEN
            )
            return response
        else:
            return super().dispatch(request, *args, **kwargs)


class PublicPostMockView(ProtectedViewMixin, BaseMockView):
    template_name = "public_post.xhtml"

    def get(self, request: Request, id: int) -> Response:
        content = self.construct_content("public", id)
        return Response(content, status=status.HTTP_200_OK)


class SubscriberPostMockView(ProtectedViewMixin, PermissionViewMixin, BaseMockView):
    template_name = "subscriber_post.xhtml"
    permissions = RoleRepository().subscriber_permissions

    def get(self, request: Request, id: int) -> Response:
        content = self.construct_content("subscriber", id)
        return Response(content, status=status.HTTP_200_OK)


class PremiumPostMockView(ProtectedViewMixin, PermissionViewMixin, BaseMockView):
    template_name = "premium_post.xhtml"
    permissions = RoleRepository().premium_subscriber_permissions

    def get(self, request: Request, id: int) -> Response:
        content = self.construct_content("premium subscriber", id)
        return Response(content, status=status.HTTP_200_OK)
