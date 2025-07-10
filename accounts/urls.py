from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),

    # Admin-only URLs
    path("user-management/", views.user_management_view, name="user_management"),
    path("delete-user/<int:user_id>/", views.delete_user_view, name="delete_user"),
    path(
        "admin/edit-user/<int:user_id>/",
        views.edit_user_admin_view,
        name="edit_user_admin",
    ),
]
