from django.db import models
from django.utils import timezone
from apps.customers.models import Customer
from apps.products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.CASCADE
    )
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending", "Pending"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
        ],
    )

    def __str__(self):
        return f"Order #{self.order_number} on {self.date}"

    def get_total_amount(self):
        return sum(item.get_total_price() for item in self.items.all())


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="orders", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.unit_price}"
