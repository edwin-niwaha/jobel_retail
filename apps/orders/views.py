from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order
from .models import Cart, CartItem, Order
from apps.products.models import Product, Volume, ProductVolume
from django.core.exceptions import MultipleObjectsReturned


# from .forms import OrderForm, SaleProcessingForm
# from apps.sales.models import Sale, SaleDetail


# =================================== Products Detail ===================================
# @login_required
# def product_detail(request, id):
#     product = get_object_or_404(Product, id=id)

#     # Retrieve or create a cart for the logged-in user
#     cart, created = Cart.objects.get_or_create(user=request.user)

#     # Calculate the total number of items in the cart
#     cart_items = CartItem.objects.filter(cart=cart)
#     cart_count = sum(item.quantity for item in cart_items)

#     # Fetch the volume associated with the product
#     # volume = product.volume  # Access the volume directly
#     volumes = Volume.objects.all()

#     context = {
#         "product": product,
#         "volume": volumes,  # Pass volume to the template
#         "cart_count": cart_count,
#     }

#     return render(request, "orders/product_detail.html", context)


# Example of updated view
@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = sum(item.quantity for item in cart_items)

    # Fetch all volumes and pass them to the template
    volumes = Volume.objects.all()

    context = {
        "product": product,
        "volumes": volumes,  # Make sure this is the correct name and is passed properly
        "cart_count": cart_count,
    }

    return render(request, "orders/product_detail.html", context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity = int(
        request.POST.get("quantity", 1)
    )  # Get quantity from POST data or default to 1

    if quantity <= 0:
        messages.add_message(
            request,
            messages.ERROR,
            "Invalid quantity. It must be greater than zero.",
            extra_tags="bg-danger text-white",
        )
        return redirect("orders:product_detail", id=product_id)

    try:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    except MultipleObjectsReturned:
        cart_item = CartItem.objects.filter(
            cart=cart, product=product
        ).first()  # Get the first item

    if not created:
        if quantity > 0:
            cart_item.quantity += quantity
            cart_item.save()
            messages.add_message(
                request,
                messages.INFO,
                f"Increased quantity of {product.name} to {cart_item.quantity} in your cart.",
                extra_tags="bg-info text-white",
            )
        else:
            cart_item.delete()
            messages.add_message(
                request,
                messages.WARNING,
                f"{product.name} has been removed from your cart.",
                extra_tags="bg-warning text-dark",
            )
    else:
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"{product.name} has been added to your cart with quantity {quantity}.",
                extra_tags="bg-success text-white",
            )
        else:
            cart_item.delete()
            messages.add_message(
                request,
                messages.WARNING,
                f"{product.name} has been removed from your cart.",
                extra_tags="bg-warning text-dark",
            )

    return redirect("orders:product_detail", id=product_id)


@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
    return redirect("orders:cart")


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "orders/cart.html", {"cart": cart})


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect("orders:cart_view")  # Redirect to cart if empty
    order = Order.objects.create(user=request.user, cart=cart)
    cart.items.all().delete()  # Clear cart items
    return redirect("orders:order_summary", order_id=order.id)


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_summary.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.all()
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.status = "PROCESSED"
        order.processed_at = timezone.now()
        order.save()
        return redirect("orders:order_list")
    return render(request, "orders/process_order.html", {"order": order})
