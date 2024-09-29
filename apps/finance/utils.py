from apps.finance.models import Transaction


def generate_ledger_report(account_id, start_date, end_date):
    transactions = Transaction.objects.filter(
        account_id=account_id, transaction_date__range=(start_date, end_date)
    ).select_related("account", "offset_account")

    statement_data = {}
    for transaction in transactions:
        account_name = transaction.account.account_name
        if account_name not in statement_data:
            statement_data[account_name] = {"debits": 0, "credits": 0, "balance": 0}

        if transaction.transaction_type == "debit":
            statement_data[account_name]["debits"] += transaction.amount
        else:
            statement_data[account_name]["credits"] += transaction.amount

    for account_name, data in statement_data.items():
        data["balance"] = data["credits"] - data["debits"]

    return statement_data
