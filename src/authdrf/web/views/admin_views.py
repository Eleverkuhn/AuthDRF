from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from authdrf.web.serializers.user_serializers import UserOutSerializer
from authdrf.web.views.base_views import (
    ProtectedViewMixin, PermissionViewMixin, BaseViewMixin
)
from authdrf.data.models.permission_models import RoleRepository


class AdminDashboardView(ProtectedViewMixin, PermissionViewMixin, BaseViewMixin, APIView):
    template_name = "admin.xhtml"
    serializer_class = UserOutSerializer
    permissions = RoleRepository().admin_permissions
