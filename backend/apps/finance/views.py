from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.db import transaction
from django.shortcuts import render, redirect
from datetime import datetime, date
from .forms import (
    ChartOfAccountsForm,
    IncomeTransactionForm,
    ExpenseTransactionForm,
    TransactionFormSet,
)
from .models import ChartOfAccounts, Transaction

from apps.authentication.decorators import (
    admin_or_manager_or_staff_required,
    admin_or_manager_required,
    admin_required,
)


# =================================== Account List view ===================================
def chart_of_accounts_list_view(request):
    accounts = ChartOfAccounts.objects.all()  # Retrieve all accounts
    accounts_by_type = {}  # Dictionary to group accounts by type

    # Group accounts by their account type
    for account in accounts:
        account_type = account.get_account_type_display()
        if account_type not in accounts_by_type:
            accounts_by_type[account_type] = []
        accounts_by_type[account_type].append(account)

    context = {
        "accounts_by_type": accounts_by_type,
        "table_title": "Chart of Accounts",
    }
    return render(request, "finance/chart_of_accounts_list.html", context)


# =================================== Add Account view ===================================
@login_required
@admin_or_manager_required
def add_chart_of_account_view(request):
    form = ChartOfAccountsForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(
            request, "Account added successfully!", extra_tags="bg-success"
        )
        return redirect("finance:add_chart_of_account")

    # Additional context for the template
    context = {
        "form": form,
        "table_title": "Add New Account",
    }

    return render(request, "finance/chart_of_account_add.html", context)


# =================================== Account update view ===================================
@login_required
@admin_or_manager_or_staff_required
@transaction.atomic
def chart_of_account_update_view(request, account_id):
    account = get_object_or_404(ChartOfAccounts, id=account_id)

    if request.method == "POST":
        form = ChartOfAccountsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Account: {account.account_name} updated successfully!",
                extra_tags="bg-success",
            )
            return redirect("finance:chart_of_accounts_list")
        else:
            messages.error(
                request,
                "There was an error updating the account!",
                extra_tags="bg-danger",
            )
    else:
        form = ChartOfAccountsForm(instance=account)

    context = {"form": form, "account": account, "page_title": "Update Account"}

    return render(request, "finance/chart_of_account_update.html", context)


# =================================== Account delete view ===================================
@login_required
@admin_required
@transaction.atomic
def chart_of_account_delete_view(request, account_id):
    account = get_object_or_404(ChartOfAccounts, id=account_id)

    try:
        account.delete()
        messages.success(
            request,
            f"Account: {account.account_name} deleted successfully!",
            extra_tags="bg-success",
        )
    except Exception as e:
        messages.error(
            request,
            "An error occurred during the deletion process.",
            extra_tags="bg-danger",
        )
        print(f"Error deleting account: {e}")

    return redirect("finance:chart_of_accounts_list")


# =================================== Income transaction creation view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def income_transaction_create_view(request):
    if request.method == "POST":
        form = IncomeTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Income transaction posted successfully.",
                extra_tags="bg-success",
            )
            return redirect("finance:income_add")
    else:
        form = IncomeTransactionForm()

    context = {
        "form": form,
        "form_title": "Add New Income Transaction",
    }

    return render(request, "finance/income_add.html", context)


# =================================== expense add view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def expense_transaction_create_view(request):
    if request.method == "POST":
        form = ExpenseTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Expense transaction posted successfully.",
                extra_tags="bg-success",
            )
            return redirect("finance:expense_add")
    else:
        form = ExpenseTransactionForm()

    context = {
        "form": form,
        "form_title": "Add New Expense Transaction",
    }

    return render(request, "finance/expense_add.html", context)


# =================================== multi-journal entry view ===================================
@login_required
@admin_or_manager_required  # Assuming this decorator is defined somewhere
@transaction.atomic
def multi_journal_view(request):
    if request.method == "POST":
        formset = TransactionFormSet(request.POST)
        transaction_date = request.POST.get(
            "transaction_date"
        )  # Capture the single transaction date

        if formset.is_valid():
            transactions = formset.save(commit=False)

            # Initialize total debits and credits
            total_debits = 0
            total_credits = 0

            for transaction in transactions:
                # Assign the captured transaction date to each transaction
                transaction.transaction_date = transaction_date

                # Calculate totals based on transaction type
                if transaction.transaction_type == "debit":
                    total_debits += transaction.amount
                elif transaction.transaction_type == "credit":
                    total_credits += transaction.amount

            # Validate that total debits equal total credits
            if total_debits != total_credits:
                messages.error(
                    request,
                    "Total debits must equal total credits.",
                    extra_tags="bg-danger",
                )
                return render(
                    request,
                    "finance/multi_journal_entry_add.html",
                    {
                        "formset": formset,
                        "form_title": "Add New Transactions",
                    },
                )

            # Save all transactions
            for transaction in transactions:
                transaction.save()

            messages.success(
                request, "Transactions posted successfully.", extra_tags="bg-success"
            )
            return redirect("finance:multi_journal")
    else:
        formset = TransactionFormSet(
            queryset=Transaction.objects.none()
        )  # Start with empty forms

    context = {
        "formset": formset,
        "form_title": "Add New Transactions",
    }

    return render(request, "finance/multi_journal_entry_add.html", context)


# =================================== ledger_report ist view ===================================
def get_financial_year_dates():
    """Returns the start and end dates for the current financial year."""
    today = date.today()

    # Check if today is after July 1st (start of the financial year)
    if today.month >= 7:
        start_date = date(today.year, 7, 1)  # July 1st of the current year
        end_date = date(today.year + 1, 6, 30)  # June 30th of the next year
    else:
        start_date = date(today.year - 1, 7, 1)  # July 1st of the previous year
        end_date = date(today.year, 6, 30)  # June 30th of the current year

    return start_date, end_date


@login_required
@admin_or_manager_required
def ledger_report_view(request):
    selected_account_id = request.GET.get("account_id")  # Get selected account ID
    ledger_data = []
    accounts = ChartOfAccounts.objects.all()  # Fetch all accounts for the dropdown
    total_debits = 0
    total_credits = 0

    # Get the start and end dates for the current financial year
    financial_year_start, financial_year_end = get_financial_year_dates()

    # Use query parameters or default to the financial year range
    start_date = request.GET.get("start_date") or financial_year_start
    end_date = request.GET.get("end_date") or financial_year_end

    selected_account = None
    opening_balance = 0

    if selected_account_id:
        selected_account = get_object_or_404(ChartOfAccounts, id=selected_account_id)

        # Get transactions within the selected date range
        ledger_data = Transaction.objects.filter(
            account=selected_account, transaction_date__range=[start_date, end_date]
        ).order_by("transaction_date")

        # Get opening balance by calculating the balance before the start_date
        opening_balance_queryset = Transaction.objects.filter(
            account=selected_account, transaction_date__lt=start_date
        )

        # Calculate the opening balance as the sum of all prior debits and credits
        for transaction in opening_balance_queryset:
            if transaction.transaction_type == "debit":
                opening_balance += transaction.amount
            elif transaction.transaction_type == "credit":
                opening_balance -= transaction.amount

        # Calculate debits, credits, and running balance
        running_balance = opening_balance
        for transaction in ledger_data:
            if transaction.transaction_type == "debit":
                transaction.debit = transaction.amount
                transaction.credit = 0
                total_debits += transaction.amount
            elif transaction.transaction_type == "credit":
                transaction.debit = 0
                transaction.credit = transaction.amount
                total_credits += transaction.amount
            else:
                transaction.debit = 0
                transaction.credit = 0

            # Update running balance
            running_balance += transaction.debit - transaction.credit
            transaction.running_balance = running_balance

    return render(
        request,
        "finance/ledger_report.html",
        {
            "ledger_data": ledger_data,
            "accounts": accounts,
            "selected_account": selected_account,
            "selected_account_id": selected_account_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_debits": total_debits,
            "total_credits": total_credits,
            "opening_balance": opening_balance,  # Pass opening balance to template
        },
    )
