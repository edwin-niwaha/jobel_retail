from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from apps.authentication.forms import LoginForm
from .views import (
    RegisterView,
    ChangePasswordView,
    CustomLoginView,
    ResetPasswordView,
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

# Define URL patterns for the application
urlpatterns = [
    # Home and Dashboard
    path("", home, name="users-home"),
    path("dashboard/", dashboard, name="dashboard"),
    # User Registration and Login
    path("register/", RegisterView.as_view(), name="users-register"),
    path(
        "login/",
        CustomLoginView.as_view(
            redirect_authenticated_user=True,
            template_name="accounts/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    # Password Management
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
    # Profile Management
    path("profile/", profile, name="users-profile"),
    path("profile-list/", profile_list, name="profile_list"),
    path("profile/update/<int:pk>/", update_profile, name="update_profile"),
    path("profile/delete/<int:pk>/", delete_profile, name="delete_profile"),
    # User Feedback
    path("contact-us/", contact_us, name="contact_us"),
    path("feedback/", user_feedback, name="user_feedback"),
    path("feedback/delete/<int:pk>/", delete_feedback, name="delete_feedback"),
    path(
        "feedback/validate/<int:contact_id>/",
        validate_user_feedback,
        name="validate_user_feedback",
    ),
    # Social Authentication
    re_path(r"^oauth/", include("social_django.urls", namespace="social")),
]
