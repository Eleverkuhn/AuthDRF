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

from authdrf.web.serializers.user_serializers import (
    UserSerializer, SignInSerializer
)
from authdrf.service.auth_services import SignUpService

type RedirectResponse = HttpResponseRedirect | HttpResponsePermanentRedirect


class BaseView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "base.xhtml"


class SignUpView(BaseView):
    template_name = "sign_up.xhtml"

    def get(self, request: Request) -> Response:
        return Response(
            {"serializer": UserSerializer(), "errors": {}},
            status=status.HTTP_200_OK
        )

    def post(self, request: Request) -> RedirectResponse:
        serializer = UserSerializer(data=request.data)
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


class SignInView(BaseView):
    template_name = "sign_in.xhtml"

    def get(self, request: Request) -> Response:
        response = Response(
            {"serializer": SignInSerializer(), "errors": {}},
            status=status.HTTP_200_OK
        )
        return response
