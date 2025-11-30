from django.urls import path, include

from authdrf.web.views.user_views import UserPageView

urlpatterns = [
    path("", UserPageView.as_view(), name="user_page"),
]
