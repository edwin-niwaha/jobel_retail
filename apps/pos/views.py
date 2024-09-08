import json
from django.http import JsonResponse
from datetime import date, timedelta
from django.db.models.functions import ExtractYear
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F
from django.db.models.functions import Coalesce
from django.shortcuts import render

from apps.products.models import Product, Category
from apps.sales.models import Sale

from apps.authentication.decorators import (
    admin_or_manager_required,
    admin_required,
    admin_or_manager_or_staff_required,
)


# =================================== Home User view  ===================================
def home(request):
    return render(request, "accounts/home.html")


def get_total_sales_for_period(start_date, end_date):
    return (
        Sale.objects.filter(trans_date__range=[start_date, end_date]).aggregate(
            total_sales=Sum("grand_total")
        )["total_sales"]
        or 0
    )


# =================================== The dashboard view ===================================
@login_required
@admin_or_manager_or_staff_required
def dashboard(request):
    today = date.today()
    year = today.year
    monthly_earnings = []

    # Calculate earnings per month
    for month in range(1, 13):
        earning = (
            Sale.objects.filter(trans_date__year=year, trans_date__month=month)
            .aggregate(
                total_variable=Coalesce(
                    Sum(F("grand_total")), 0.0, output_field=FloatField()
                )
            )
            .get("total_variable")
        )
        monthly_earnings.append(earning)

    # Calculate annual earnings
    annual_earnings = (
        Sale.objects.filter(trans_date__year=year)
        .aggregate(
            total_variable=Coalesce(
                Sum(F("grand_total")), 0.0, output_field=FloatField()
            )
        )
        .get("total_variable")
    )
    annual_earnings = format(annual_earnings, ".2f")

    # AVG per month
    avg_month = format(sum(monthly_earnings) / 12, ".2f")

    # Total sales for today, week, and month
    def get_total_sales_for_period(start_date, end_date):
        return (
            Sale.objects.filter(trans_date__range=[start_date, end_date]).aggregate(
                total_sales=Coalesce(
                    Sum(F("grand_total")), 0.0, output_field=FloatField()
                )
            )["total_sales"]
            or 0
        )

    total_sales_today = get_total_sales_for_period(today, today)
    start_of_week = today - timedelta(days=today.weekday())
    total_sales_week = get_total_sales_for_period(start_of_week, today)
    start_of_month = today.replace(day=1)
    total_sales_month = get_total_sales_for_period(start_of_month, today)

    # Top-selling products
    top_products = Product.objects.annotate(
        quantity_sum=Sum("saledetail__quantity")
    ).order_by("-quantity_sum")[:3]

    top_products_data = [(p.name, p.quantity_sum) for p in top_products]

    # Ensure default values are included if no products are available
    top_products_data += [("None", 0)] * (3 - len(top_products_data))

    top_products_names = [name for name, _ in top_products_data]
    top_products_quantity = [quantity for _, quantity in top_products_data]

    # Stock balances
    stock_bal = Product.objects.filter(status="ACTIVE")  # Only active products

    context = {
        "active_icon": "dashboard",
        "products": Product.objects.filter(status="ACTIVE").count(),
        "total_stock": stock_bal.aggregate(Sum("stock"))["stock__sum"],
        "categories": Category.objects.all().count(),
        "annual_earnings": annual_earnings,
        "monthly_earnings": json.dumps(monthly_earnings),
        "avg_month": avg_month,
        "total_sales_today": total_sales_today,
        "total_sales_week": total_sales_week,
        "total_sales_month": total_sales_month,
        "top_products_names": json.dumps(top_products_names),
        "top_products_names_list": top_products_data,
        "top_products_quantity": json.dumps(top_products_quantity),
    }
    return render(request, "pos/dashboard.html", context)


# =================================== Monthly earnings graph ===================================
# @login_required
# @admin_or_manager_or_staff_required
# def monthly_earnings_view(request):
#     today = date.today()
#     year = today.year
#     monthly_earnings = []

#     for month in range(1, 13):
#         earning = (
#             Sale.objects.filter(date_added__year=year, date_added__month=month)
#             .aggregate(
#                 total_variable=Coalesce(
#                     Sum(F("grand_total")), 0.0, output_field=FloatField()
#                 )
#             )
#             .get("total_variable")
#         )
#         monthly_earnings.append(earning)

#     return JsonResponse(
#         {
#             "labels": [
#                 "Jan",
#                 "Feb",
#                 "Mar",
#                 "Apr",
#                 "May",
#                 "Jun",
#                 "Jul",
#                 "Aug",
#                 "Sep",
#                 "Oct",
#                 "Nov",
#                 "Dec",
#             ],
#             "data": monthly_earnings,
#         }
#     )


@login_required
@admin_or_manager_or_staff_required
def monthly_earnings_view(request):
    today = date.today()
    year = today.year
    monthly_earnings = []

    for month in range(1, 13):
        earning = (
            Sale.objects.filter(trans_date__year=year, trans_date__month=month)
            .aggregate(
                total_variable=Coalesce(
                    Sum(F("grand_total")), 0.0, output_field=FloatField()
                )
            )
            .get("total_variable")
        )
        monthly_earnings.append(earning)

    return JsonResponse(
        {
            "labels": [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
            "data": monthly_earnings,
        }
    )


# =================================== Annual Sales graph ===================================
def sales_data_api(request):
    # Query to get total sales grouped by year
    sales_per_year = (
        Sale.objects.annotate(year=ExtractYear("trans_date"))
        .values("year")
        .annotate(total_sales=Sum("grand_total"))
        .order_by("year")
    )

    # Prepare the data as a dictionary
    data = {
        "years": [item["year"] for item in sales_per_year],
        "total_sales": [item["total_sales"] for item in sales_per_year],
    }

    # Return the data as JSON
    return JsonResponse(data)
