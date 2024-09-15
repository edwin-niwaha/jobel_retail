from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    # cart
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "remove_from_cart/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    # orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/process/", views.process_order, name="process_order"),
]
