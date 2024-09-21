from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product, ProductVolume
from apps.customers.models import Customer


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def checkout(self, payment_method, total_amount):
        order = Order.objects.create(
            user=self.user,
            total_amount=total_amount,
            payment_method=payment_method,
            status="Pending",
        )
        for item in self.items.all():
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.volume.price,
            )
        self.items.all().delete()  # Clear the cart after checkout
        return order


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
    # Link to Customer instead of directly to User for both online and offline customers
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="Cash"
    )

    def __str__(self):
        # Use customer full name regardless of online or offline
        return f"Order {self.id} by {self.customer.full_name()}"


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="details", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.price
