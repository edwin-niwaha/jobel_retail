import json
import logging
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.wsgi import *
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from apps.customers.models import Customer
from apps.products.models import Product, ProductVolume
from .models import Sale, SaleDetail
from .forms import ReportPeriodForm
from django.db.models import Prefetch


# Import custom decorators
from apps.authentication.decorators import (
    admin_or_manager_or_staff_required,
    admin_or_manager_required,
    admin_required,
)

logger = logging.getLogger(__name__)


# =================================== Sale list view ===================================
@login_required
@admin_or_manager_or_staff_required
def sales_list_view(request):
    # sales = (
    #     Sale.objects.all()
    #     .select_related("customer")
    #     .prefetch_related("items")
    #     .order_by("id")
    # )
    sales = (
        Sale.objects.all()
        .select_related("customer")
        .prefetch_related(
            "items__product__productvolume_set__volume"  # Follow the relationship chain to get the volume
        )
        .order_by("id")
    )

    grand_total = sales.aggregate(Sum("grand_total"))["grand_total__sum"] or 0
    total_items = sum(sale.sum_items() for sale in sales)  # As before, calling method

    context = {
        "table_title": "sales",
        "sales": sales,
        "grand_total": grand_total,
        "total_items": total_items,
    }

    return render(request, "sales/sales.html", context=context)


# =================================== sales_report_view view ===================================
@admin_or_manager_or_staff_required
@login_required
def sales_report_view(request):
    # Initialize the form with GET data (if available)
    form = ReportPeriodForm(request.GET)

    # Default date range values
    start_date = None
    end_date = None

    # If the form is valid, use the cleaned data
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        # Use default dates if no valid form data
        start_date = None
        end_date = None

    # Filter sales by the selected date range
    # sales = Sale.objects.filter(trans_date__range=[start_date, end_date])

    sales = Sale.objects.filter(trans_date__range=[start_date, end_date]).prefetch_related(
        'items__product__productvolume_set'  # Correct prefetch related to the Product and ProductVolume
    )

    # Aggregate totals
    total_sales = sales.aggregate(
        total_revenue=Sum('grand_total'),
        total_items_sold=Sum('items__quantity'),
        total_transactions=Count('id')
    )

    # Prepare detailed sales data
    sale_details = []
    stock_balance = 0
    total_profit_after_sales = 0  # Initialize total profit after sales

    for sale in sales:
        items = sale.items.select_related('product').all()
        # items = sale.items.select_related('product').prefetch_related('items__product__productvolume_set__volume').all()
        item_details = []
        sale_profit = 0 
        for item in items:
            product = item.product
            inventory = getattr(product, 'inventory', None)  # Get inventory if it exists
            if inventory:
                stock_balance += inventory.quantity
            
            # Calculate profit for the current sale's item (selling price - cost price)
            for volume in product.productvolume_set.all():
                item_profit = (volume.price - volume.cost) * item.quantity
                sale_profit += item_profit  # Add to sale's total profit
                total_profit_after_sales += item_profit  # Add to total profit after sales

            item_details.append({
                'product': item.product.name,
                'volume': volume.volume.ml, 
                'price': item.price,
                'quantity': item.quantity,
                'total': item.total_detail,
            })

        sale_details.append({
            'trans_date': sale.trans_date,
            'customer': f"{sale.customer.first_name} {sale.customer.last_name}" if sale.customer else "N/A",
            'grand_total': sale.grand_total,
            'profit': sale_profit,  # Add calculated profit for this sale
            'payment_method': sale.payment_method,
            'item_details': item_details,
        })

    # Prepare the context for rendering the template
    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_sales['total_revenue'],
        'total_items_sold': total_sales['total_items_sold'],
        'total_transactions': total_sales['total_transactions'],
        'sales': sale_details,
        'stock_balance': stock_balance,
        'total_profit_after_sales': total_profit_after_sales,  # Include the calculated profit
        'table_title': "Sales Report"
    }

    return render(request, 'sales/sales_report.html', context)


# =================================== Sale add view ===================================
@admin_or_manager_or_staff_required
@login_required
# def sales_add_view(request):
#     # Fetch only active products with their inventory
#     products = Product.objects.filter(status="ACTIVE").select_related("inventory")
# products = Product.objects.filter(status="ACTIVE").prefetch_related(
#     Prefetch('productvolume_set', queryset=ProductVolume.objects.select_related('volume'))
# )
#     context = {
#         "customers": [c.to_select2() for c in Customer.objects.all()],
#         "products": products,
#         "total_stock": sum(
#             product.inventory.quantity if hasattr(product, "inventory") else 0
#             for product in products
#         ),
#     }

#     if request.method == "POST":
#         try:
#             logger.debug(f"POST data: {request.POST}")

#             # Extract and process form data
#             customer_id = int(request.POST.get("customer"))
#             sale_attributes = {
#                 "customer": Customer.objects.get(id=customer_id),
#                 "trans_date": request.POST.get("trans_date"),
#                 "sub_total": float(request.POST.get("sub_total", 0)),
#                 "grand_total": float(request.POST.get("grand_total", 0)),
#                 "tax_amount": float(request.POST.get("tax_amount", 0)),
#                 "tax_percentage": float(request.POST.get("tax_percentage", 0)),
#                 "amount_payed": float(request.POST.get("amount_payed", 0)),
#                 "amount_change": float(request.POST.get("amount_change", 0)),
#             }

#             with transaction.atomic():
#                 # Create the sale
#                 new_sale = Sale.objects.create(**sale_attributes)
#                 logger.info(f"Sale created successfully: {sale_attributes}")

#                 # Extract product details from form data
#                 products_data = request.POST.getlist("products")
#                 for product_data_str in products_data:
#                     product_data = json.loads(product_data_str)
#                     product_obj = Product.objects.get(id=int(product_data["id"]))
#                     quantity_requested = int(product_data["quantity"])

#                     # Check if the product has inventory and stock is available
#                     if (
#                         not hasattr(product_obj, "inventory")
#                         or product_obj.inventory.quantity < quantity_requested
#                     ):
#                         raise ValueError(
#                             f"Oops! Insufficient stock for {product_obj.name}"
#                         )

#                     # Update inventory stock
#                     inventory_obj = product_obj.inventory
#                     inventory_obj.quantity -= quantity_requested
#                     inventory_obj.save()
#                     logger.info(
#                         f"Stock updated for {product_obj.name}: {inventory_obj.quantity}"
#                     )

#                     # Create sale detail
#                     detail_attributes = {
#                         "sale": new_sale,
#                         "product": product_obj,
#                         "price": float(product_data["price"]),
#                         "quantity": quantity_requested,
#                         "total_detail": float(product_data["total_product"]),
#                     }
#                     SaleDetail.objects.create(**detail_attributes)
#                     logger.info(f"Sale detail added: {detail_attributes}")

#                 messages.success(
#                     request, "Sale created successfully!", extra_tags="bg-success"
#                 )
#                 return redirect("sales:sales_list")

#         except ValueError as ve:
#             logger.error(f"Stock error: {ve}")
#             messages.error(request, str(ve), extra_tags="danger")
#         except Exception as e:
#             logger.error(f"Error during sale creation: {e}")
#             messages.error(
#                 request,
#                 f"There was an error during the creation! Error: {e}",
#                 extra_tags="danger",
#             )

#         return redirect("sales:sales_list")

#     return render(request, "sales/sales_add.html", context=context)

def sales_add_view(request):
    # Fetch products with active status and related inventory
    products = Product.objects.filter(status="ACTIVE").select_related("inventory").prefetch_related("productvolume_set")

    # Prepare context for rendering
    context = {
        "customers": [c.to_select2() for c in Customer.objects.all()],
        "products": products,
        "total_stock": sum(
            product.inventory.quantity if hasattr(product, "inventory") else 0
            for product in products
        ),
    }

    if request.method == "POST":
        try:
            logger.debug(f"POST data: {request.POST}")

            # Extract and process form data
            customer_id = int(request.POST.get("customer"))
            sale_attributes = {
                "customer": Customer.objects.get(id=customer_id),
                "trans_date": request.POST.get("trans_date"),
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
                products_data = request.POST.getlist("products")
                for product_data_str in products_data:
                    product_data = json.loads(product_data_str)

                    # Parse combined product and volume IDs
                    product_id, volume_id = map(int, product_data["id"].split("-"))
                    product_obj = Product.objects.get(id=product_id)
                    quantity_requested = int(product_data["quantity"])

                    # Check if the product's inventory has sufficient stock
                    if (
                        not hasattr(product_obj, "inventory")
                        or product_obj.inventory.quantity < quantity_requested
                    ):
                        raise ValueError(
                            f"Oops! Insufficient stock for {product_obj.name}"
                        )

                    # Update inventory stock at the product level
                    inventory_obj = product_obj.inventory
                    inventory_obj.quantity -= quantity_requested
                    inventory_obj.save()
                    logger.info(
                        f"Stock updated for {product_obj.name}: {inventory_obj.quantity}"
                    )

                    # Create sale detail
                    detail_attributes = {
                        "sale": new_sale,
                        "product": product_obj,
                        "price": float(product_data["price"]),
                        "quantity": quantity_requested,
                        "total_detail": float(product_data["total_product"]),
                    }
                    SaleDetail.objects.create(**detail_attributes)
                    logger.info(f"Sale detail added: {detail_attributes}")

                # Success message
                messages.success(
                    request, "Sale created successfully!", extra_tags="bg-success"
                )
                return redirect("sales:sales_add")

        except ValueError as ve:
            logger.error(f"Stock error: {ve}")
            messages.error(request, str(ve), extra_tags="bg-danger")
        except Exception as e:
            logger.error(f"Error during sale creation: {e}")
            messages.error(
                request,
                f"There was an error during the creation! Error: {e}",
                extra_tags="bg-danger",
            )

        return redirect("sales:sales_add")

    return render(request, "sales/sales_add.html", context=context)


# =================================== Sale details view ===================================
@login_required
@admin_or_manager_or_staff_required
def sales_details_view(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    # Get the sale details related to the sale
    details = SaleDetail.objects.filter(sale=sale)

    context = {
        "active_icon": "sales",
        "sale": sale,
        "details": details,
    }

    return render(request, "sales/sales_details.html", context=context)


# =================================== Sale delete view ===================================
@login_required
@admin_required
@transaction.atomic
def sale_delete_view(request, sale_id):
    try:
        # Get the sale to delete
        sale = Sale.objects.get(id=sale_id)
        sale.delete()
        messages.success(
            request, f"Sale: {sale_id} deleted successfully!", extra_tags="bg-success"
        )
    except Sale.DoesNotExist:
        # Specific exception for when the sale is not found
        messages.error(
            request,
            f"Sale: {sale_id} not found!",
            extra_tags="bg-danger",
        )
    except Exception as e:
        # General exception for any other errors
        messages.error(
            request,
            "There was an error during the elimination!",
            extra_tags="bg-danger",
        )
        print(e)
    finally:
        return redirect("sales:sales_list")


# =================================== Sale receipt view ===================================
@login_required
@admin_or_manager_or_staff_required
def receipt_pdf_view(request, sale_id):
    # Get the sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    # Render the template
    template = get_template("sales/sales_receipt_pdf.html")
    context = {"sale": sale, "details": details}
    html_template = template.render(context)

    # Create a file-like buffer to receive PDF data
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="receipt.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html_template, dest=response)

    # Check if PDF was created successfully
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response
