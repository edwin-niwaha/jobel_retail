from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("add-account/", views.add_chart_of_account_view, name="add_chart_of_account"),
    path("accounts/", views.chart_of_accounts_list_view, name="chart_of_accounts_list"),
    path("import-accounts/", views.import_coa_data, name="import_coa_data"),

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
    path("profit-and-loss/", views.profit_and_loss_view, name="profit_and_loss"),
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
    path("multi-journal/", views.multi_journal_view, name="multi_journal"),
    path("ledger_report/", views.ledger_report_view, name="ledger_report"),  # No ID
    path(
        "ledger_report/<int:account_id>/",
        views.ledger_report_view,
        name="ledger_report_with_id",
    ),  # With ID
]
