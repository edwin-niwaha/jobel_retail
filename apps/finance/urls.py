from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("add-account/", views.add_chart_of_account_view, name="add_chart_of_account"),
    path("accounts/", views.chart_of_accounts_list_view, name="chart_of_accounts_list"),
    path(
        "update/<str:account_id>/",
        views.chart_of_account_update_view,
        name="chart_of_account_update",
    ),
    path(
        "delete/<str:account_id>/",
        views.chart_of_account_delete_view,
        name="chart_of_account_delete",
    ),
    path(
        "income/add/",
        views.income_transaction_create_view,
        name="income_add",
    ),
    path(
        "expense/add/",
        views.expense_transaction_create_view,
        name="expense_add",
    ),
    path("ledger_report/", views.ledger_report_view, name="ledger_report"),  # No ID
    path(
        "ledger_report/<int:account_id>/",
        views.ledger_report_view,
        name="ledger_report_with_id",
    ),  # With ID
]
