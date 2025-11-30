from django.urls import path, include

from authdrf.web.views.main_views import MainView

urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("auth/", include("authdrf.web.urls.auth_urls")),
    path("my/", include("authdrf.web.urls.user_urls")),
]
