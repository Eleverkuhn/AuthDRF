from rest_framework import status

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request


class BaseViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name: str
    serializer_class: type[Serializer]

    def get(self, request: Request) -> Response:
        return Response(
            {"serializer": self.serializer_class}, status=status.HTTP_200_OK
        )
