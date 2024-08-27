from django.urls import path
from .views import (
    RegisterView,
    contact_us,
    delete_profile,
    home,
    dashboard,
    profile,
    profile_list,
    update_profile,
    validate_user_feedback,
    user_feedback,
    delete_feedback,
)

urlpatterns = [
    path("", home, name="users-home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("register/", RegisterView.as_view(), name="users-register"),
    # Profile
    path("profile/", profile, name="users-profile"),
    path("profile-list/", profile_list, name="profile_list"),
    path("profile/update/<int:pk>", update_profile, name="update_profile"),
    path("profile/delete/<int:pk>", delete_profile, name="delete_profile"),
    # User Feedback
    path("contact-us/", contact_us, name="contact_us"),
    path("feedback/", user_feedback, name="user_feedback"),
    path("feedback/delete/<int:pk>", delete_feedback, name="delete_feedback"),
    path(
        "feedback/validate/<int:contact_id>/",
        validate_user_feedback,
        name="validate_user_feedback",
    ),
]
