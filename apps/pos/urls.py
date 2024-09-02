from django.urls import path

from . import views

urlpatterns = [
    # Home
    path("", views.home, name="users-home"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/monthly_earnings/",
        views.monthly_earnings_view,
        name="monthly_earnings_view",
    ),
]
