from django.urls import path

from authdrf.web.views.auth_views import (
    SignUpView, SignInView, RefreshTokenView, SignOutView
)


urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("sign-in/", SignInView.as_view(), name="sign_in"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
]
