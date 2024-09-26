from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from django.shortcuts import render, redirect
from .forms import ChartOfAccountsForm
from .models import ChartOfAccounts

from apps.authentication.decorators import (
    admin_or_manager_or_staff_required,
    admin_or_manager_required,
    admin_required,
)


# =================================== Account List view ===================================
# @login_required
# @admin_or_manager_or_staff_required
# def chart_of_accounts_list_view(request):
#     accounts = ChartOfAccounts.objects.all()
#     context = {
#         "accounts": accounts,
#         "table_title": "Chart of Accounts",
#     }
#     return render(request, "finance/chart_of_accounts_list.html", context)


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
