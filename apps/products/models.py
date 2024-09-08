from django.db import models
from django.forms import model_to_dict

# Define choices for product status
STATUS_CHOICES = [
    ("", "-- Choose status --"),
    ("ACTIVE", "Active"),
    ("INACTIVE", "Inactive"),
]

# Define choices for gender
GENDER_CHOICES = [
    ("", "-- Choose gender --"),
    ("Unisex", "Unisex"),
    ("Male", "Male"),
    ("Female", "Female"),
]

# Define choices for product type
PRODUCT_TYPE_CHOICES = [
    ("", "-- Choose product type --"),
    ("Roll-On", "Roll-On"),
    ("Spray", "Spray"),
]


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
    )
    description = models.CharField(
        max_length=255, blank=True, verbose_name="Description"
    )

    class Meta:
        db_table = "category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=256, verbose_name="Product Name")
    description = models.TextField(verbose_name="Product Description")
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=10, verbose_name="Status"
    )
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Category",
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=10,
        default="Unisex",
        verbose_name="Targeted Gender",
    )
    product_type = models.CharField(
        choices=PRODUCT_TYPE_CHOICES,
        max_length=10,
        default="Spray",
        verbose_name="Product Type",
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Cost Price"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Selling Price"
    )
    stock = models.PositiveIntegerField(verbose_name="Stock Quantity")
    low_stock_threshold = models.PositiveIntegerField(
        default=5, verbose_name="Low Stock Threshold"
    )
    is_out_of_stock = models.BooleanField(default=False, verbose_name="Out of Stock")

    class Meta:
        db_table = "product"

    def __str__(self):
        return self.name

    def check_stock_alerts(self):
        """Check stock levels and update alerts."""
        if self.stock <= 0:
            self.is_out_of_stock = True
        else:
            self.is_out_of_stock = False
        if self.stock <= self.low_stock_threshold:
            # Trigger a low stock alert
            self.send_low_stock_alert()

    def send_low_stock_alert(self):
        """Send an alert for low stock."""
        # Implement your notification logic here
        # For example, sending an email or logging the alert
        pass

    def save(self, *args, **kwargs):
        self.check_stock_alerts()
        super().save(*args, **kwargs)

    def to_json(self):
        item = model_to_dict(self)
        item.update(
            {
                "id": self.id,
                "text": self.name,
                "category": self.category.name if self.category else None,
                "quantity": 1,
                "total_product": 0,
            }
        )
        return item

    @property
    def prefixed_id(self):
        return f"JBL{self.pk:03d}"
