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
        "order-confirmation/<int:order_id>/",
        views.order_confirmation_view,
        name="order_confirmation",
    ),
    # orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/process/", views.process_order, name="process_order"),
]
