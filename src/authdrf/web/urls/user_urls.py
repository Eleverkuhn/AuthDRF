from django.urls import path

from authdrf.web.views.user_views import UserPageView, ChangePasswordView

urlpatterns = [
    path("", UserPageView.as_view(), name="user_page"),
    path("password/", ChangePasswordView.as_view(), name="change_password"),
]
