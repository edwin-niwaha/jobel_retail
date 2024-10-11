from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Inventory
from .forms import InventoryForm
from apps.products.models import Product

from apps.authentication.decorators import (
    admin_or_manager_or_staff_required,
    admin_or_manager_required,
    admin_required,
)


@login_required
@admin_or_manager_or_staff_required
def inventory_list_view(request):
    inventories = Inventory.objects.select_related("product").all()
    context = {
        "inventories": inventories,
        "table_title": "Inventory List",
    }
    return render(request, "inventory/inventory_list.html", context)


@login_required
@admin_or_manager_or_staff_required
def inventory_report_view(request):
    # Fetch all inventories with related products
    inventories = Inventory.objects.select_related("product").all()

    # Calculate total stock from inventory quantities
    total_stock = inventories.aggregate(total_stock=Sum("quantity"))["total_stock"] or 0

    # Prepare context for rendering
    context = {
        "active_icon": "inventory",
        "inventories": inventories,  # Ensure this matches what the template expects
        "total_stock": total_stock,
        "table_title": "Inventory Report",
    }

    return render(request, "inventory/inventory_report.html", context=context)


@login_required
@admin_or_manager_or_staff_required
def inventory_add_view(request):
    context = {
        "table_title": "Add Inventory",
    }
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Inventory added successfully!", extra_tags="bg-success"
            )
            return redirect(
                "inventory:inventory_list"
            )  # Adjust the redirect as necessary
    else:
        form = InventoryForm()
        context["form"] = form

    return render(request, "inventory/inventory_add.html", context=context)


@login_required
@admin_or_manager_or_staff_required
def inventory_update_view(request, pk):
    context = {
        "table_title": "Update Inventory",
    }
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Inventory updated successfully!", extra_tags="bg-success"
            )
            return redirect("inventory:inventory_list")
    else:
        form = InventoryForm(instance=inventory)
        context["form"] = form
    return render(request, "inventory/inventory_update.html", context=context)


@login_required
@admin_required
def inventory_delete_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inventory.delete()
        messages.success(
            request, "Inventory deleted successfully!", extra_tags="bg-warning"
        )
        return redirect("inventory:inventory_list")
    return render(
        request, "inventory/inventory_confirm_delete.html", {"inventory": inventory}
    )
