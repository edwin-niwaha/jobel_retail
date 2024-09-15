from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# =================================== customers model ===================================
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Last Name"
    )
    address = models.TextField(
        max_length=50, blank=True, null=True, verbose_name="Address"
    )
    email = models.EmailField(
        max_length=30, blank=True, null=True, verbose_name="Email"
    )
    phone = PhoneNumberField(
        null=True,
        blank=True,
        default="+256999999999",
        verbose_name="Business Telephone",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        db_table = "Customers"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def to_select2(self):
        return {"label": self.get_full_name(), "value": self.id}
