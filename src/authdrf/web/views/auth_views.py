from django.contrib import messages
from django.shortcuts import redirect
from django.http.response import (
    HttpResponseRedirect, HttpResponsePermanentRedirect
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.validators import ValidationError
from rest_framework.serializers import Serializer

from authdrf.exc import AuthenticationError
from authdrf.web.serializers.user_serializers import (
    UserSerializer, SignInSerializer
)
from authdrf.service.auth_services import SignUpService, SignInService

type RedirectResponse = HttpResponseRedirect | HttpResponsePermanentRedirect


class BaseViewMixin:
    renderer_classes = [TemplateHTMLRenderer]
    template_name: str
    serializer_class: type[Serializer]

    def get(self, request: Request) -> Response:
        return Response(
            {"serializer": self.serializer_class}, status=status.HTTP_200_OK
        )


class SignUpView(BaseViewMixin, APIView):
    template_name = "sign_up.xhtml"
    serializer_class = UserSerializer

    def post(self, request: Request) -> RedirectResponse | Response:
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(
                {"serializer": serializer, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            service = SignUpService(serializer.validated_data)
            service.exec()
            messages.success(request, service.success_message())
            return redirect("main")


class SignInView(BaseViewMixin, APIView):
    template_name = "sign_in.xhtml"
    serializer_class = SignInSerializer

    def post(self, request: Request) -> RedirectResponse | Response:
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"serializer": serializer})
        else:
            response = self._sign_in_user(serializer)
            return response

    def _sign_in_user(
            self, serializer: SignInSerializer
    ) -> RedirectResponse | Response:
        service = SignInService(redirect("main"), serializer.validated_data)
        try:
            response = service.exec()
        except AuthenticationError as error:
            return Response(
                {"serializer": serializer, "error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return response
