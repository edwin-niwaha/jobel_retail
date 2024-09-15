# cart/models.py
from django.db import models
from django.conf import settings
from apps.products.models import Product, ProductVolume


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    volume = models.ForeignKey(
        ProductVolume, on_delete=models.CASCADE
    )  # Link to the correct volume
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.volume.volume.ml}ML (x{self.quantity})"

    def get_total_price(self):
        return self.volume.price * self.quantity  # Use volume's price


# Constants for choices
ORDER_STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
]
PAYMENT_METHOD_CHOICES = [
    ("Cash", "Cash"),
    ("Credit Card", "Credit Card"),
    ("Bank Transfer", "Bank Transfer"),
]


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="Pending"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    shipping_address = models.TextField()
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True
    )
    payment_status = models.CharField(max_length=20, default="UNPAID")
    tracking_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def get_total_amount(self):
        return sum(item.get_total_price() for item in self.cart.items.all())

    def is_paid(self):
        return self.payment_status == "PAID"

    def mark_as_shipped(self):
        if self.status in ["PROCESSED", "SHIPPED"]:
            raise ValueError("Order is already processed or shipped.")
        self.status = "SHIPPED"
        self.save()

    def mark_as_delivered(self):
        if self.status != "SHIPPED":
            raise ValueError(
                "Order must be shipped before it can be marked as delivered."
            )
        self.status = "DELIVERED"
        self.save()
