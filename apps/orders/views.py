from django.contrib import messages
import logging
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from .models import Order
from .models import Cart, CartItem, Order, OrderDetail
from apps.products.models import Product, ProductVolume
from django.core.exceptions import MultipleObjectsReturned
from .forms import CheckoutForm, OrderStatusForm
from apps.customers.models import Customer

from apps.authentication.decorators import (
    admin_or_manager_required,
    admin_required,
    admin_or_manager_or_staff_required,
)

logger = logging.getLogger(__name__)


# =================================== Products Detail ===================================
@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = sum(item.quantity for item in cart_items)

    # Fetch volumes specific to this product
    product_volumes = ProductVolume.objects.filter(product=product)

    context = {
        "product": product,
        "product_volumes": product_volumes,  # Pass product-specific volumes to the template
        "cart_count": cart_count,
    }

    return render(request, "orders/product_detail.html", context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get("quantity", 1))
    volume_id = request.POST.get("volume_id")

    # Validate the volume
    if not volume_id:
        messages.error(request, "Please select a product volume.")
        return redirect("orders:product_detail", id=product_id)

    # Fetch the selected volume
    volume = get_object_or_404(ProductVolume, id=volume_id)

    if quantity <= 0:
        messages.add_message(
            request,
            messages.ERROR,
            "Invalid quantity. It must be greater than zero.",
            extra_tags="bg-danger text-white",
        )
        return redirect("orders:product_detail", id=product_id)

    try:
        # Add volume to the CartItem creation or retrieval
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, volume=volume
        )
    except MultipleObjectsReturned:
        cart_item = CartItem.objects.filter(
            cart=cart, product=product, volume=volume
        ).first()

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.add_message(
            request,
            messages.INFO,
            f"Increased quantity of {product.name} ({volume.volume.ml} ML) to {cart_item.quantity} in your cart.",
            extra_tags="bg-info text-white",
        )
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            f"{product.name} ({volume.volume.ml} ML) has been added to your cart with quantity {quantity}.",
            extra_tags="bg-success text-white",
        )

    return redirect("orders:product_detail", id=product_id)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    total_price = sum(item.get_total_price() for item in cart.items.all())

    context = {
        "cart": cart,
        "total_price": total_price,
    }

    return render(request, "orders/cart.html", context)


@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect(
            "orders:cart_view"
        )  # Redirect to cart view if the cart is empty

    # Get or create a customer entry for the current user
    customer, created = Customer.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            total_amount = cart.get_total_price()

            # Update the customer's information from the form
            customer.first_name = form.cleaned_data["first_name"]
            customer.last_name = form.cleaned_data["last_name"]
            customer.email = form.cleaned_data["email"]
            customer.phone = form.cleaned_data["phone"]
            customer.address = form.cleaned_data["address"]
            customer.save()  # Save the updated customer information

            # Create the order
            order = Order.objects.create(
                customer=customer,
                created_at=timezone.now(),
                total_amount=total_amount,
                status="Pending",  # Or set a default status
                payment_method=payment_method,
            )

            # Create OrderDetail entries for each item in the cart
            for item in cart.items.all():
                # item.volume refers to the ProductVolume
                OrderDetail.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.volume.price,  # Use price from ProductVolume
                )

            # Clear the cart items after checkout
            cart.items.all().delete()

            # Optionally, redirect to an order confirmation page
            messages.success(
                request,
                f"Your order has been placed successfully! Order ID: {order.id}",
            )
            return redirect("orders:order_confirmation", order_id=order.id)

    else:
        # Prepopulate the form with existing customer data if available
        form = CheckoutForm(
            initial={
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
            }
        )

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/order_confirmation.html", {"order": order})


@login_required
@admin_or_manager_or_staff_required
def orders_to_be_processed_view(request):
    orders = Order.objects.filter(status__in=["Pending", "Shipped"]).order_by(
        "created_at"
    )

    table_title = "Orders to be Processed"

    return render(
        request,
        "orders/orders_to_be_processed.html",
        {"orders": orders, "table_title": table_title},
    )


@login_required
def customer_order_history_view(request):
    try:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer).order_by("-created_at")

        return render(request, "orders/order_history.html", {"orders": orders})

    except ObjectDoesNotExist:
        messages.error(
            request, "You do not have a customer profile associated with your account."
        )
        return redirect("users-home")


@login_required
@admin_or_manager_or_staff_required
def all_orders_view(request):
    status_filter = request.GET.get("status", "")
    if status_filter == "All" or status_filter == "":
        orders = Order.objects.all().order_by("-created_at")
    else:
        orders = Order.objects.filter(status=status_filter)

    context = {
        "orders": orders,
        "status_filter": status_filter,
    }
    return render(request, "orders/all_orders.html", context)


@login_required
def order_report_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("details"), id=order_id)

    print("Order Details Count:", order.details.count())
    for detail in order.details.all():
        print(detail.product.name, detail.quantity, detail.price)

    return render(request, "orders/order_report.html", {"order": order})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
@admin_or_manager_or_staff_required
def order_process_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("details"), id=order_id)

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Order status updated successfully!", extra_tags="bg-success"
            )
            return redirect("orders:orders_to_be_processed")
        else:
            # Extract error messages
            error_messages = [
                f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()
            ]
            formatted_errors = " ".join(error_messages)
            messages.error(
                request,
                f"Failed to update order status: {formatted_errors}",
                extra_tags="bg-danger",
            )

    else:
        form = OrderStatusForm(instance=order)

    return render(request, "orders/order_process.html", {"order": order, "form": form})
