from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from authdrf.web.views.base_views import ProtectedViewMixin, PermissionViewMixin
from authdrf.data.models.permission_models import RoleRepository


class BaseMockView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def construct_content(self, post_type: str, id: int) -> dict[str, str]:
        return {"mock_object": f"Example of {post_type} level post with id {id}"}


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
