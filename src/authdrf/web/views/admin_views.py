from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from logger.setup import LoggingConfig
from authdrf.web.views.base_views import (
    ProtectedViewMixin, PermissionViewMixin, ExtendedHTTPView
)
from authdrf.service.admin_services import AdminDashboardService
from authdrf.data.models.permission_models import RoleRepository


class AdminDashboardView(ProtectedViewMixin, PermissionViewMixin, ExtendedHTTPView):
    service = AdminDashboardService

    @property
    def permissions(self) -> list[str]:
        return RoleRepository().admin_permissions

    def get_response(self, content: dict) -> Response:
        return Response(content, status=status.HTTP_200_OK)


class AdminDashboardPermissionsView(AdminDashboardView):
    template_name = "admin_permissions.xhtml"

    def get(self, request: Request) -> Response:
        return self.construct_response()

    def post(self, request: Request) -> Response:
        self.service(request.data).add_permission()
        response = self.construct_response()
        return response

    def delete(self, request: Request) -> Response:
        self.service(request.data).delete_permission()
        response = self.construct_response()
        return response

    def construct_response(self) -> Response:
        content = self.service.construct_permissions_content()
        response = self.get_response(content)
        return response


class AdminDashboardRolesView(AdminDashboardView):
    template_name = "admin_roles.xhtml"

    def get(self, request: Request) -> Response:
        return self.construct_response()

    def patch(self, request: Request) -> Response:
        self.service(request.data).add_permission_to_role()
        response = self.construct_response()
        return response

    def delete(self, request: Request) -> Response:
        self.service(request.data).delete_role()
        response = self.construct_response()
        return response

    def construct_response(self) -> Response:
        content = self.service.construct_roles_content()
        response = self.get_response(content)
        return response


class AdminDashboardUsersView(AdminDashboardView):
    template_name = "admin_users.xhtml"

    def get(self, request: Request) -> Response:
        return self.construct_response()

    def patch(self, request: Request) -> Response:
        self.service(request.data).change_user_role()
        response = self.construct_response()
        return response

    def construct_response(self) -> Response:
        content = self.service.construct_users_content()
        response = self.get_response(content)
        return response
