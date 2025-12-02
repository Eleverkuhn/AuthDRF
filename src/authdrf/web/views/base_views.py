from rest_framework import status

from django.http.response import (
    HttpResponseRedirect, HttpResponsePermanentRedirect
)
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from logger.setup import LoggingConfig
from authdrf.exc import AuthorizationError, RefreshRequired, PermissionError
from authdrf.service.auth_services import (
    AuthorizationService, PermissionService
)


type RedirectResponse = HttpResponseRedirect | HttpResponsePermanentRedirect


class BaseViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name: str
    serializer_class: type[Serializer]

    def get(self, request: Request) -> Response:
        content = {"serializer": self.serializer_class}
        return Response(content, status=status.HTTP_200_OK)


class ExtendedHTTPView(APIView):
    def post(self, request: Request) -> Response | RedirectResponse:
        if request.POST.get("_method") == "PUT":
            return self.put(request)
        if request.POST.get("_method") == "DELETE":
            return self.delete(request)
        if request.POST.get("_method") == "PATCH":
            return self.patch(request)


class ProtectedViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "response_401.xhtml"

    def dispatch(self, request: Request, *args, **kwargs):
        try:
            user = AuthorizationService(request.COOKIES).exec()
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
            request.user = user
            return super().dispatch(request, *args, **kwargs)

    def _construct_refresh_url(self, request: Request) -> str:
        requested_url = request.build_absolute_uri()
        url = "".join([reverse("refresh"), f"?next={requested_url}"])
        return url


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
