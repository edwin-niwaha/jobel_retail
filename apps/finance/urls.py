from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("add-account/", views.add_chart_of_account_view, name="add_chart_of_account"),
    path("accounts/", views.chart_of_accounts_list_view, name="chart_of_accounts_list"),
    # Update customer
    path(
        "update/<str:account_id>/",
        views.chart_of_account_update_view,
        name="chart_of_account_update",
    ),
    # Delete customer
    path(
        "delete/<str:account_id>/",
        views.chart_of_account_delete_view,
        name="chart_of_account_delete",
    ),
]
