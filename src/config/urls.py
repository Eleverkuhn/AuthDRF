from django.urls import path, include

from authdrf.web.views.main_views import MainView
from authdrf.web.views.business_mock_views import (
    PublicPostMockView,
    SubscriberPostMockView,
    PremiumPostMockView
)
from authdrf.web.views.admin_views import AdminDashboardView

urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("auth/", include("authdrf.web.urls.auth_urls")),
    path("my/", include("authdrf.web.urls.user_urls")),
    path("public/<int:id>/", PublicPostMockView.as_view(), name="public_post"),
    path("sub/<int:id>/", SubscriberPostMockView.as_view(), name="subscriber_post"),
    path("premium/<int:id>/", PremiumPostMockView.as_view(), name="premium_post"),
    path("admin/", AdminDashboardView.as_view(), name="admin"),
]
