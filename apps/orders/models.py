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


class Order(models.Model):
    # Constants for choices
    ORDER_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Canceled", "Canceled"),
        ("Refunded", "Refunded"),
        ("Returned", "Returned"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("Mobile Money", "Mobile Money"),
        # ('Visa', 'Visa Payment'),
        # ('MasterCard', 'MasterCard Payment'),
        # ('PayPal', 'PayPal Payment'),
        # Add more options as necessary
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="MTN MOMO"
    )
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    external_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        # Use customer full name regardless of online or offline
        return f"Order {self.id} by {self.customer.full_name()}"

    def calculate_totals(self):
        """
        Calculate total amounts, tax, and change based on order details.
        This method should be called whenever order details are updated.
        """
        subtotal = sum(detail.total for detail in self.details.all())
        self.total_amount = subtotal + self.tax_amount
        self.amount_change = self.amount_paid - self.total_amount
        self.save()  # Save updated totals to the database


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="details", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.price
