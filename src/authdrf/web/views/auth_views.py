from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer


class SignUpView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "sign_up.xhtml"

    def get(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)
