from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

# Import models and forms
from .models import Category, Product
from .forms import CategoryForm, ProductForm


# Import custom decorators
from apps.authentication.decorators import (
    admin_or_manager_or_staff_required,
    admin_or_manager_required,
    admin_required,
)


# =================================== categories view ===================================
@login_required
@admin_or_manager_or_staff_required
def categories_list_view(request):
    context = {
        "active_icon": "products_categories",
        "categories": Category.objects.all(),
    }
    return render(request, "products/categories.html", context=context)


# =================================== categories add view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def categories_add_view(request):
    context = {
        "active_icon": "products_categories",
        "category_status": Category.STATUS_CHOICES,  # Use STATUS_CHOICES instead of the field choice
    }

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Check if a category with the same name already exists
            category_name = form.cleaned_data["name"]
            if Category.objects.filter(name=category_name).exists():
                messages.error(
                    request,
                    f"A category with the name '{category_name}' already exists.",
                    extra_tags="warning",
                )
            else:
                try:
                    # Save the form data
                    form.save()
                    messages.success(
                        request,
                        f"Category: {category_name} created successfully!",
                        extra_tags="bg-success",
                    )
                    return redirect("products:categories_list")
                except Exception as e:
                    messages.error(
                        request,
                        "There was an error during the creation!",
                        extra_tags="bg-danger",
                    )
                    print(e)
                    return redirect("products:categories_add")
        else:
            messages.error(
                request,
                "Please correct the errors below.",
                extra_tags="warning",
            )
    else:
        form = CategoryForm()

    context["form"] = form
    return render(request, "products/categories_add.html", context=context)


# =================================== categories update view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def categories_update_view(request, category_id):

    # Get the category or return a 404 error if not found
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                # Save the form data
                form.save()
                messages.success(
                    request,
                    f"Category: {form.cleaned_data['name']} updated successfully!",
                    extra_tags="bg-success",
                )
                return redirect("products:categories_list")
            except Exception as e:
                messages.error(
                    request,
                    "There was an error during the update!",
                    extra_tags="bg-danger",
                )
                print(e)
                return redirect("products:categories_list")
        else:
            messages.error(
                request,
                "Please correct the errors below.",
                extra_tags="warning",
            )
    else:
        form = CategoryForm(instance=category)

    context = {
        "active_icon": "products_categories",
        "category_status": Category.STATUS_CHOICES,  # Use STATUS_CHOICES instead of the field choice
        "form": form,
        "category": category,
    }

    return render(request, "products/categories_update.html", context=context)


# =================================== categories delete view ===================================
@admin_required
@transaction.atomic
def categories_delete_view(request, category_id):

    try:
        # Get the category to delete
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(
            request,
            "¡Category: " + category.name + " deleted!",
            extra_tags="bg-success",
        )
        return redirect("products:categories_list")
    except Exception as e:
        messages.success(
            request,
            "There was an error during the elimination!",
            extra_tags="bg-danger",
        )
        print(e)
        return redirect("products:categories_list")


# =================================== produts list view ===================================
@login_required
@admin_or_manager_or_staff_required
def products_list_view(request):
    products = Product.objects.all()
    total_price = sum(product.price for product in products)

    context = {
        "active_icon": "products",
        "products": products,
        "total_price": total_price,
    }

    return render(request, "products/products.html", context=context)


# =================================== products add view ===================================
@login_required
@admin_or_manager_or_staff_required
@transaction.atomic
def products_add_view(request):
    context = {
        "active_icon": "products_categories",
        "product_status": Product.status.field.choices,
        "categories": Category.objects.filter(status="ACTIVE"),
    }

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # Check if a product with the same attributes exists
            attributes = form.cleaned_data
            if Product.objects.filter(**attributes).exists():
                messages.error(
                    request, "Product already exists!", extra_tags="bg-warning"
                )
                return redirect("products:products_add")

            try:
                form.save()
                messages.success(
                    request,
                    f"Product: {attributes['name']} created successfully!",
                    extra_tags="bg-success",
                )
                return redirect("products:products_list")
            except Exception as e:
                messages.error(
                    request,
                    "There was an error during the creation!",
                    extra_tags="bg-danger",
                )
                print(e)
                return redirect("products:products_add")
        else:
            messages.error(
                request,
                "There were errors in the form submission.",
                extra_tags="bg-danger",
            )
    else:
        form = ProductForm()

    context["form"] = form
    return render(request, "products/products_add.html", context=context)


# =================================== products update view ===================================
@login_required
@admin_or_manager_or_staff_required
@transaction.atomic
def products_update_view(request, product_id):
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, id=product_id)

    context = {
        "active_icon": "products",
        "product_status": Product.status.field.choices,
        "product": product,
        "categories": Category.objects.all(),
    }

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            # Check if a product with the same attributes exists, excluding the current product
            attributes = form.cleaned_data
            if Product.objects.filter(**attributes).exclude(id=product_id).exists():
                messages.error(
                    request,
                    "Product with the same attributes already exists!",
                    extra_tags="warning",
                )
                return redirect("products:products_update", product_id=product_id)

            try:
                form.save()
                messages.success(
                    request,
                    f"Product: {product.name} updated successfully!",
                    extra_tags="bg-success",
                )
                return redirect("products:products_list")
            except Exception as e:
                messages.error(
                    request,
                    "There was an error during the update!",
                    extra_tags="bg-danger",
                )
                print(e)
                return redirect("products:products_update", product_id=product_id)
        else:
            messages.error(
                request,
                "There were errors in the form submission.",
                extra_tags="bg-danger",
            )
    else:
        form = ProductForm(instance=product)

    context["form"] = form
    return render(request, "products/products_update.html", context=context)


# =================================== products delete view ===================================
@login_required
@admin_required
@transaction.atomic
def products_delete_view(request, product_id):
    try:
        # Get the product to delete
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(
            request, "¡Product: " + product.name + " deleted!", extra_tags="bg-success"
        )
        return redirect("products:products_list")
    except Exception as e:
        messages.success(
            request,
            "There was an error during the elimination!",
            extra_tags="bg-danger",
        )
        print(e)
        return redirect("products:products_list")


def is_ajax(request):
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


