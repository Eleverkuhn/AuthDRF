from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from logger.setup import LoggingConfig
from authdrf.web.views.base_views import (
    ProtectedViewMixin, PermissionViewMixin, ExtendedHTTPView
)
from authdrf.service.admin_services import AdminDashboardService
from authdrf.data.models.permission_models import RoleRepository


class AdminDashboardUsersView(ProtectedViewMixin, PermissionViewMixin, ExtendedHTTPView):
    template_name = "admin_users.xhtml"
    service = AdminDashboardService

    @property
    def permissions(self) -> list[str]:
        return RoleRepository().admin_permissions

    def get(self, request: Request) -> Response:
        response = self.construct_response()
        return response

    def patch(self, request: Request) -> Response:
        LoggingConfig().logger.debug(request.data)
        self.service(request.data).change_user_role()
        response = self.construct_response()
        return response

    def construct_response(self) -> Response:
        content = self.service.construct_content()
        response = Response(content, status=status.HTTP_200_OK)
        return response
