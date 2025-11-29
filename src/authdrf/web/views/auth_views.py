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

from authdrf.service.auth_services import SignUpService

type RedirectResponse = HttpResponseRedirect | HttpResponsePermanentRedirect


class SignUpView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "sign_up.xhtml"

    def get(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)

    def post(self, request: Request) -> RedirectResponse:
        SignUpService(request.data).exec()
        messages.success(request, SignUpService.success_message())
        return redirect("main")
