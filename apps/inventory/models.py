from django.db import models
from apps.products.models import Product


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(verbose_name="Stock Quantity", default=0)
    low_stock_threshold = models.PositiveIntegerField(
        default=5, verbose_name="Low Stock Threshold"
    )
    is_out_of_stock = models.BooleanField(default=False, verbose_name="Out of Stock")

    def check_stock_alerts(self):
        """Check stock levels and update stock status."""
        self.is_out_of_stock = self.quantity <= 0

        # Trigger low stock alert if quantity is less than or equal to threshold
        if self.quantity <= self.low_stock_threshold and not self.is_out_of_stock:
            self.send_low_stock_alert()

    def send_low_stock_alert(self):
        """Send an alert for low stock."""
        # Implement notification logic here
        # For example, sending an email or logging the alert
        print(
            f"Low stock alert for {self.product.name}. Current stock: {self.quantity}"
        )

    def save(self, *args, **kwargs):
        # Ensure stock alerts are checked before saving
        self.check_stock_alerts()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Stock: {self.quantity}"
