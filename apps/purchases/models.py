from django.db import models
from django.utils import timezone
from apps.products.models import Product


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Unpaid", "Unpaid"),
        ("Partially Paid", "Partially Paid"),
    ]

    purchase_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(
        Supplier, related_name="purchases", on_delete=models.CASCADE
    )
    purchase_date = models.DateField()
    invoice_number = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Unpaid"
    )
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def get_total_amount(self):
        return sum(detail.get_total_cost() for detail in self.details.all())

    def __str__(self):
        return f"Purchase {self.purchase_id} - {self.supplier.name}"


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(
        Purchase, related_name="details", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="purchase_details", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_cost(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.unit_price}"
