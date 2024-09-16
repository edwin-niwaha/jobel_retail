from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order
from .models import Cart, CartItem, Order
from apps.products.models import Product, ProductVolume
from django.core.exceptions import MultipleObjectsReturned
from .forms import CheckoutForm

# from apps.sales.models import Sale, SaleDetail


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
        )  # Redirect to cart view if cart does not exist

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            total_amount = cart.get_total_price()

            # Create an order
            order = cart.checkout(
                payment_method=payment_method, total_amount=total_amount
            )

            # Optionally, you can redirect to an order confirmation page
            messages.success(
                request,
                f"Your order has been placed successfully! Order ID: {order.id}",
            )
            return redirect("orders:order_confirmation", order_id=order.id)

    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


# ////////////////////////////
@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/order_confirmation.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.all()
    return render(request, "orders/orders.html", {"orders": orders})


@login_required
def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.status = "PROCESSED"
        order.processed_at = timezone.now()
        order.save()
        return redirect("orders:order_list")
    return render(request, "orders/process_order.html", {"order": order})
