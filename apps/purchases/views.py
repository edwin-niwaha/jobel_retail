from django.shortcuts import render
from django.db.models import Sum
from .models import Purchase
from apps.sales.models import Sale


def generate_profit_loss_report(start_date, end_date):
    # Total Sales Revenue
    total_revenue = (
        Sale.objects.filter(date__range=[start_date, end_date]).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    # Total COGS
    purchases = Purchase.objects.filter(date__range=[start_date, end_date])
    total_cogs = sum(
        item.get_total_cost() for purchase in purchases for item in purchase.items.all()
    )

    # Gross Profit
    gross_profit = total_revenue - total_cogs

    # Assuming operating expenses are stored somewhere
    operating_expenses = 0  # Replace this with actual expense calculation

    # Net Profit
    net_profit = gross_profit - operating_expenses

    return {
        "total_revenue": total_revenue,
        "total_cogs": total_cogs,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "net_profit": net_profit,
    }
