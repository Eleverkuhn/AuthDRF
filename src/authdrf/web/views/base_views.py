from rest_framework import status

from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request

from authdrf.exc import AuthorizationError, RefreshRequired
from authdrf.service.auth_services import (
    AuthorizationService, RefreshTokenService
)


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

    def dispatch(self, request: Request, *args, **kwargs):
        try:
            AuthorizationService(request.COOKIES).exec()
        except RefreshRequired:
            url = self._construct_refresh_url(request)
            return redirect(reverse("refresh"), url)
        except AuthorizationError as error:
            response = render(
                request,
                "response_401.xhtml",
                {"error": str(error)},
                status=status.HTTP_401_UNAUTHORIZED
            )
            return response
        else:
            return super().dispatch(request, *args, **kwargs)

    def _construct_refresh_url(self, request: Request) -> str:
        requested_url = request.build_absolute_uri()
        url = "".join([reverse("refresh"), f"?next={requested_url}"])
        return url
