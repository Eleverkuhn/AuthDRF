from rest_framework import status

from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request

from authdrf.exc import AuthorizationError
from authdrf.service.auth_services import AuthorizationService


class BaseViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name: str
    serializer_class: type[Serializer]

    def get(self, request: Request) -> Response:
        return Response(
            {"serializer": self.serializer_class}, status=status.HTTP_200_OK
        )


class ProtectedViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "response_401.xhtml"

    def dispatch(self, request, *args, **kwargs):
        try:
            AuthorizationService(request.COOKIES).exec()
        except AuthorizationError as error:
            # return Response({"error": str(error)}, status=status.HTTP_401_UNAUTHORIZED)
            # return HttpResponse(str(error), status=status.HTTP_401_UNAUTHORIZED)
            response = render(
                request,
                "response_401.xhtml",
                {"error": str(error)},
                status=status.HTTP_401_UNAUTHORIZED
            )
            return response
        else:
            return super().dispatch(request, *args, **kwargs)
