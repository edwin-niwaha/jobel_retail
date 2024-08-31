from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
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

    # @property
    # def prefixed_id(self):
    #     if self.pk < 10:
    #         return f"JBL00{self.pk}"
    #     elif self.pk < 100:
    #         return f"JBL0{self.pk}"
    #     else:
    #         return f"JBL{self.pk}"
