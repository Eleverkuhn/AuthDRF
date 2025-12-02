from django.urls import path

from authdrf.web.views.admin_views import (
    AdminDashboardUsersView, AdminDashboardPermissionsView, AdminDashboardRolesView
)


urlpatterns = [
    path("users/", AdminDashboardUsersView.as_view(), name="admin_users"),
    path(
        "permissions/",
        AdminDashboardPermissionsView.as_view(),
        name="admin_permissions"
    ),
    path("roles/", AdminDashboardRolesView.as_view(), name="admin_roles")
]
