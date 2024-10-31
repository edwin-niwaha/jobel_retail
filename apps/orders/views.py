from django.contrib import messages
import requests
from django.http import JsonResponse
import logging
from django.conf import settings
import base64
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from .models import Order, PAYMENT_METHOD_CHOICES
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


# Process payment
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form_title = "Payment Details"

    # Payment method choices to be displayed in the form
    payment_method_choices = PAYMENT_METHOD_CHOICES

    if request.method == "POST":
        payment_method = request.POST.get(
            "payment_method"
        )  # Capture the payment method
        phone_number = request.POST.get("phone_number")  # Capture the phone number

        # Log payment method for debugging
        logger.debug(f"Payment Method: {payment_method}, Phone Number: {phone_number}")

        # Prepare payment request data
        payment_data = {
            "amount": float(order.total_amount),
            "currency": "USD",  # Change this to your currency if necessary
            "externalId": str(order.id),  # Unique identifier for the transaction
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number,  # The phone number of the payer
            },
            "payerMessage": f"Payment for Order #{order.id}",
            "payeeMessage": "Payment received",
        }

        # Prepare headers for API request
        access_token = get_access_token(
            settings.MTN_CLIENT_ID, settings.MTN_CLIENT_SECRET
        )  # Function to get the token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Request to MTN's API to initiate payment
        request_to_pay_url = (
            "https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"
        )
        try:
            response = requests.post(
                request_to_pay_url, headers=headers, json=payment_data
            )
            response.raise_for_status()  # Raise an error for bad responses
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            order.payment_status = "failed"
            order.save()
            return JsonResponse(
                {"error": "Payment failed due to server error. Please try again."}
            )
        except Exception as err:
            logger.error(f"An error occurred: {err}")
            order.payment_status = "failed"
            order.save()
            return JsonResponse(
                {"error": "An unexpected error occurred. Please try again."}
            )

        if response.status_code == 200:
            transaction_info = response.json()
            order.transaction_id = transaction_info.get("transactionId")
            order.payment_status = "pending"  # Set status to pending
            order.save()

            # Optionally redirect or return a success response
            return redirect("orders:customer_order_history")
        else:
            order.payment_status = "failed"
            order.save()
            return JsonResponse({"error": "Payment failed. Please try again."})

    return render(
        request,
        "orders/payment.html",
        {
            "order": order,
            "form_title": form_title,
            "payment_method_choices": payment_method_choices,  # Pass payment methods to template
        },
    )


def get_access_token(client_id, client_secret):
    url = "https://sandbox.momodeveloper.mtn.com/collection/token/"
    # Prepare Basic Authentication Header
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Failed to retrieve access token: {http_err}")
        return None  # Handle this case as per your logic
    except Exception as err:
        logger.error(f"An error occurred while fetching the access token: {err}")
        return None  # Handle this case as per your logic

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token")
    else:
        logger.error(
            f"Failed to retrieve access token: {response.status_code}, {response.text}"
        )
        return None  # Handle this case as per your logic


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
