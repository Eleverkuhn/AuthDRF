from django.urls import path

from authdrf.web.views.auth_views import SignUpView, SignInView


urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("sign-in/", SignInView.as_view(), name="sign_in"),
]
