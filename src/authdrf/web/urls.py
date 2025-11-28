from django.urls import path

from authdrf.web.views.auth_views import SignUpView


urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
]
