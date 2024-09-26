from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum, F, Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F
from apps.inventory.models import Inventory

# Import models and forms
from .models import Category, Volume, ProductVolume, Product, ProductImage
from .forms import (
    CategoryForm,
    VolumeForm,
    ProductVolumeForm,
    ProductForm,
    ProductImageForm,
)


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
        "form": form,
        "category": category,
    }

    return render(request, "products/categories_update.html", context=context)


# =================================== categories delete view ===================================
@login_required
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


# # =================================== volumes(ML) List view ===================================
def volume_list(request):
    volumes = Volume.objects.all()
    return render(request, "products/volume_ml_list.html", {"volumes": volumes})


# # =================================== volumes(ML) add view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def volume_add_view(request):
    if request.method == "POST":
        form = VolumeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Volume added successfully.", extra_tags="bg-success"
            )
            return redirect("products:volume_add")  # Redirect to a list or detail view
    else:
        form = VolumeForm()

    return render(request, "products/volume_ml.html", {"form": form, "action": "Add"})


# # =================================== volumes(ML) update view ===================================
@login_required
@admin_or_manager_required
@transaction.atomic
def volume_update_view(request, volume_id):
    volume = get_object_or_404(Volume, id=volume_id)
    if request.method == "POST":
        form = VolumeForm(request.POST, instance=volume)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Volume updated successfully.", extra_tags="bg-success"
            )
            return redirect("products:volume_list")  # Redirect to a list or detail view
    else:
        form = VolumeForm(instance=volume)

    return render(
        request, "products/volume_ml_update.html", {"form": form, "action": "Update"}
    )


# =================================== Product volumes view ===================================
@login_required
@admin_or_manager_or_staff_required
def product_volume_list_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_volumes = ProductVolume.objects.filter(product=product)

    # Calculate totals
    total_ml = sum(volume.volume.ml for volume in product_volumes)
    total_cost = sum(volume.cost for volume in product_volumes)
    total_price = sum(volume.price for volume in product_volumes)

    context = {
        "product": product,
        "product_volumes": product_volumes,
        "total_ml": total_ml,
        "total_cost": total_cost,
        "total_price": total_price,
    }

    return render(request, "products/volumes.html", context)


# =================================== Product volumes add view ===================================
@login_required
@admin_or_manager_or_staff_required
@transaction.atomic
def add_product_volume_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductVolumeForm(request.POST, product=product)
        if form.is_valid():
            volume_id = form.cleaned_data[
                "volume"
            ].id  # assuming the volume field is called 'volume'
            if ProductVolume.objects.filter(
                product=product, volume_id=volume_id
            ).exists():
                form.add_error(
                    None, "Oops! This volume is already associated with the product."
                )
            else:
                try:
                    form.save()  # Save will use the product passed in the form
                    messages.success(request, "Volume added successfully!")
                    return redirect(
                        "products:product_volume_list", product_id=product.id
                    )
                except IntegrityError:
                    form.add_error(None, "An unexpected error occurred while saving.")
    else:
        form = ProductVolumeForm(product=product)

    return render(
        request, "products/volumes_add.html", {"form": form, "product": product}
    )


# # =================================== Product volumes update view ===================================
@login_required
@admin_or_manager_or_staff_required
def update_product_volume_view(request, product_id, volume_id):
    # Fetch the related product and product volume
    product = get_object_or_404(Product, id=product_id)
    product_volume = get_object_or_404(ProductVolume, id=volume_id, product=product)

    # Handle form submission
    if request.method == "POST":
        form = ProductVolumeForm(request.POST, instance=product_volume, product=product)
        if form.is_valid():
            form.save()
            return redirect("products:product_volume_list", product_id=product.id)
    else:
        # Pre-fill the form with existing product volume data
        form = ProductVolumeForm(instance=product_volume, product=product)

    # Render the update form template
    return render(
        request, "products/volumes_update.html", {"form": form, "product": product}
    )


# ================================ Product delete volume =================================
@login_required
@admin_required
@transaction.atomic
def delete_product_volume_view(request, volume_id):
    product_volume = get_object_or_404(ProductVolume, id=volume_id)
    product_id = product_volume.product.id
    product_volume.delete()
    return redirect("products:product_volume_list", product_id=product_id)


@login_required
@admin_or_manager_or_staff_required
def products_list_all(request):
    # Fetch products with prefetch_related for volumes and images
    products = Product.objects.prefetch_related("productvolume_set", "images").all()

    # Calculate totals using inventory quantities
    total_stock = sum(
        product.inventory.quantity for product in products if product.inventory
    )

    total_ml = (
        products.aggregate(total_ml=Sum("productvolume__volume__ml"))["total_ml"] or 0
    )
    total_cost = (
        products.aggregate(total_cost=Sum("productvolume__cost"))["total_cost"] or 0
    )
    total_price = (
        products.aggregate(total_price=Sum("productvolume__price"))["total_price"] or 0
    )

    context = {
        "products": products,
        "total_stock": total_stock,
        "total_ml": total_ml,
        "total_cost": total_cost,
        "total_price": total_price,
    }

    return render(request, "products/products_list_all.html", context)


# =================================== produts list view ===================================


@login_required
@admin_or_manager_or_staff_required
def products_list_view(request):
    # Fetch all products with related volumes and inventory
    products = Product.objects.prefetch_related("productvolume_set", "inventory").all()

    # Calculate total price and total cost using inventory quantity
    total_price = (
        ProductVolume.objects.filter(product__inventory__isnull=False).aggregate(
            total_price=Sum(F("price") * F("product__inventory__quantity"))
        )["total_price"]
        or 0
    )

    total_cost = (
        ProductVolume.objects.filter(product__inventory__isnull=False).aggregate(
            total_cost=Sum(F("cost") * F("product__inventory__quantity"))
        )["total_cost"]
        or 0
    )

    # Calculate total stock from the Inventory model
    total_stock = (
        Product.objects.aggregate(total_stock=Sum("inventory__quantity"))["total_stock"]
        or 0
    )

    context = {
        "products": products,
        "total_price": total_price,
        "total_cost": total_cost,
        "total_stock": total_stock,
        "table_title": "Products",
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
        "table_title": "Add Product",
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
        "table_title": "Update Product",
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


# =================================== Stock alerts view ===================================
@login_required
@admin_or_manager_or_staff_required
def stock_alerts_view(request):
    # Fetch all products with inventory details
    low_stock_products = Inventory.objects.filter(
        quantity__lte=F("low_stock_threshold"), quantity__gt=0  # Low stock but not 0
    ).select_related(
        "product"
    )  # Ensures related product data is fetched

    out_of_stock_products = Inventory.objects.filter(
        quantity=0  # Out of stock
    ).select_related("product")

    context = {
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
    }

    return render(request, "products/stock_alerts.html", context)


# =================================== Upload Product Image ===================================
@login_required
@admin_or_manager_or_staff_required
@transaction.atomic
def update_product_image(request):
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            product_id = request.POST.get("id")
            product_image = get_object_or_404(Product, id=product_id)

            # Save the new product image without committing
            new_picture = form.save(commit=False)
            new_picture.product = product_image
            new_picture.is_default = True  # Assuming is_current means default image
            new_picture.save()

            # Update product's profile image
            product_image.image = new_picture.image
            product_image.save()

            messages.success(
                request, "Product image updated successfully!", extra_tags="bg-success"
            )
            return redirect("products:update_product_image")
        else:
            messages.error(request, "Form is invalid.", extra_tags="bg-danger")
    else:
        form = ProductImageForm()

    # Fetch all products
    products = Product.objects.all().order_by("id")

    return render(
        request,
        "products/product_image_add.html",
        {
            "form": form,
            "form_name": "Upload Product Image",
            "products": products,
            "table_title": "Upload Image",
        },
    )


# =================================== View Product Image ===================================
@login_required
@admin_or_manager_or_staff_required
def product_images(request):
    products = Product.objects.all().order_by("id")

    if request.method == "POST":
        product_id = request.POST.get("id")

        if product_id:
            selected_product = get_object_or_404(Product, id=product_id)
            # Fetch all images related to the product
            image_fetched = ProductImage.objects.filter(product_id=product_id)

            if not image_fetched.exists():
                messages.error(
                    request,
                    "No images found for the selected product.",
                    extra_tags="bg-warning",
                )

            return render(
                request,
                "products/product_images.html",
                {
                    "table_title": "Product Images",
                    "products": products,
                    "selected_product": selected_product,  # Pass the selected product
                    "product_image_fetched": image_fetched,  # Pass the fetched images
                },
            )
        else:
            messages.error(request, "No product selected.", extra_tags="bg-danger")

    # Handle GET request or fallback if no product is selected
    return render(
        request,
        "products/product_images.html",
        {"table_title": "Product Image", "products": products},
    )


# =================================== Delete Product Image ===================================
@login_required
@admin_required
@transaction.atomic
def delete_product_image(request, pk):
    records = ProductImage.objects.get(id=pk)
    records.delete()
    messages.info(request, "Record deleted successfully!", extra_tags="bg-danger")
    return HttpResponseRedirect(reverse("products:product_images"))
