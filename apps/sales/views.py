import json
import logging
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from django.db.models import Sum
from apps.customers.models import Customer
from apps.products.models import Product

# from weasyprint import HTML, CSS
from .models import Sale, SaleDetail

logger = logging.getLogger(__name__)


@login_required
def sales_list_view(request):
    sales = Sale.objects.all().select_related("customer").order_by("id")
    grand_total = sales.aggregate(Sum("grand_total"))["grand_total__sum"] or 0
    total_items = sum(sale.sum_items() for sale in sales)  # As before, calling method

    context = {
        "active_icon": "sales",
        "sales": sales,
        "grand_total": grand_total,
        "total_items": total_items,
    }

    return render(request, "sales/sales.html", context=context)


@login_required
def sales_add_view(request):
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()],
        "products": Product.objects.all(),
    }

    if request.method == "POST":
        try:
            # Log the raw POST data
            logger.debug(f"POST data: {request.POST}")

            # Extract and process form data
            customer_id = int(request.POST.get("customer"))
            sale_attributes = {
                "customer": Customer.objects.get(id=customer_id),
                "sub_total": float(request.POST.get("sub_total", 0)),
                "grand_total": float(request.POST.get("grand_total", 0)),
                "tax_amount": float(request.POST.get("tax_amount", 0)),
                "tax_percentage": float(request.POST.get("tax_percentage", 0)),
                "amount_payed": float(request.POST.get("amount_payed", 0)),
                "amount_change": float(request.POST.get("amount_change", 0)),
            }

            with transaction.atomic():
                # Create the sale
                new_sale = Sale.objects.create(**sale_attributes)
                logger.info(f"Sale created successfully: {sale_attributes}")

                # Extract product details from form data
                products = request.POST.getlist("products")
                for product in products:
                    product_data = json.loads(product)
                    detail_attributes = {
                        "sale": new_sale,
                        "product": Product.objects.get(id=int(product_data["id"])),
                        "price": float(product_data["price"]),
                        "quantity": int(product_data["quantity"]),
                        "total_detail": float(product_data["total_product"]),
                    }
                    SaleDetail.objects.create(**detail_attributes)
                    logger.info(f"Sale detail added: {detail_attributes}")

                messages.success(
                    request, "Sale created successfully!", extra_tags="bg-success"
                )
                return redirect("sales:sales_list")

        except Exception as e:
            logger.error(f"Error during sale creation: {e}")
            messages.error(
                request,
                f"There was an error during the creation! Error: {e}",
                extra_tags="danger",
            )

        return redirect("sales:sales_list")

    return render(request, "sales/sales_add.html", context=context)


@login_required
def sales_details_view(request, sale_id):
    # Get the sale using get_object_or_404 to handle cases where the sale might not exist
    sale = get_object_or_404(Sale, id=sale_id)

    # Get the sale details related to the sale
    details = SaleDetail.objects.filter(sale=sale)

    context = {
        "active_icon": "sales",
        "sale": sale,
        "details": details,
    }

    return render(request, "sales/sales_details.html", context=context)


@login_required
def receipt_pdf_view(request, sale_id):
    # Get the sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {"sale": sale, "details": details}
    html_template = template.render(context)

    # CSS Boostrap
    css_url = os.path.join(
        settings.BASE_DIR, "static/css/receipt_pdf/bootstrap.min.css"
    )

    # Create the pdf
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    return HttpResponse(pdf, content_type="application/pdf")
