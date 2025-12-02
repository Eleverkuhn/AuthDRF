from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from authdrf.web.views.base_views import ProtectedViewMixin


class PublicPostMockView(ProtectedViewMixin, APIView):
    template_name = "public_post.xhtml"

    def get(self, request: Request, id: int) -> Response:
        content = {"mock_object": f"Example of public post with id {id}"}
        return Response(content, status=status.HTTP_200_OK)
