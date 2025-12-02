from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from authdrf.exc import AuthenticationError, UserAlreadyExists
from authdrf.web.views.base_views import (
    BaseViewMixin, RedirectResponse, ProtectedViewMixin
)
from authdrf.web.serializers.user_serializers import (
    UserSerializer, SignInSerializer
)
from authdrf.service.auth_services import (
    SignUpService, SignInService, RefreshTokenService, SignOutService
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
            response = self.sign_up_user(request, serializer)
            return response

    def sign_up_user(
            self, request: Request, serializer: UserSerializer
    ) -> Response | RedirectResponse:
        try:
            service = SignUpService(serializer.validated_data)
            service.exec()
        except UserAlreadyExists as error:
            return Response({"serializer": serializer, "error": str(error)})
        else:
            return redirect("sign_in")


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
        redirect_response = redirect("user_page")
        service = SignInService(redirect_response, serializer.validated_data)
        try:
            response = service.exec()
        except AuthenticationError as error:
            return Response(
                {"serializer": serializer, "error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return response


class RefreshTokenView(APIView):
    def get(self, request: Request) -> Response:
        response = redirect(request.query_params.get("next"))
        response = RefreshTokenService(request, response).exec()
        return response


class SignOutView(ProtectedViewMixin, APIView):
    def post(self, request: Request) -> Response:
        response = redirect("sign_in")
        SignOutService(response).exec()
        return response
