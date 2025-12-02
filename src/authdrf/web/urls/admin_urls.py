from django.urls import path

from authdrf.web.views.admin_views import AdminDashboardUsersView

urlpatterns = [
    path("users/", AdminDashboardUsersView.as_view(), name="admin_users"),
]
