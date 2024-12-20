from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    # cart
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "order/<int:order_id>/process_payment/",
        views.process_payment,
        name="process_payment",
    ),
    path(
        "order-confirmation/<int:order_id>/",
        views.order_confirmation_view,
        name="order_confirmation",
    ),
    # orders
    path(
        "order-history/",
        views.customer_order_history_view,
        name="customer_order_history",
    ),
    path("cashier-orders/", views.all_orders_view, name="all_orders"),
    path("<int:order_id>/", views.order_detail_view, name="order_detail_view"),
    path(
        "to-be-processed/",
        views.orders_to_be_processed_view,
        name="orders_to_be_processed",
    ),
    path("delete/<int:order_id>/", views.order_delete_view, name="delete_order"),
    path("report/<int:order_id>/", views.order_report_view, name="order_report"),
    path("process/<int:order_id>/", views.order_process_view, name="order_process"),
    path(
        "confirm-payment/<int:order_id>/",
        views.confirm_payment_view,
        name="confirm_payment",
    ),
    path("payment/flutter/", views.payment_flutter_view, name="payment_flutter"),
]
