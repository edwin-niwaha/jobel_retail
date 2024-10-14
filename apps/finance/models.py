from django.core.exceptions import ValidationError
from django.db import models


# =================================== ChartOfAccounts Model ===================================
class ChartOfAccounts(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("asset", "Asset"),
        ("liability", "Liability"),
        ("equity", "Equity"),
        ("revenue", "Revenue"),
        ("expense", "Expense"),
    ]

    account_name = models.CharField(max_length=255, verbose_name="Account Name")
    account_type = models.CharField(
        max_length=50, choices=ACCOUNT_TYPE_CHOICES, verbose_name="Account Type"
    )
    account_number = models.CharField(
        max_length=20, unique=True, verbose_name="Account Number"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        verbose_name = "Chart of Account"
        verbose_name_plural = "Chart of Accounts"
        ordering = ["account_number"]
        db_table = "chart_of_accounts"

    def __str__(self):
        return f"{self.account_name} ({self.get_account_type_display()})"

    def clean(self):
        # Validate that the account number is numeric
        if not self.account_number.isdigit():
            raise ValidationError(
                "Account number must contain only numeric characters."
            )

        # Ensure that the account type is a valid choice
        if self.account_type not in dict(self.ACCOUNT_TYPE_CHOICES).keys():
            raise ValidationError(f"Invalid account type: {self.account_type}")

        # Additional custom validations can be added here if necessary

    def save(self, *args, **kwargs):
        # Run the clean method before saving
        self.clean()
        super().save(*args, **kwargs)


# =================================== Transaction Model ===================================
TRANSACTION_TYPE_CHOICES = [
    ("debit", "Debit"),
    ("credit", "Credit"),
]


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    account = models.ForeignKey(
        "ChartOfAccounts", on_delete=models.CASCADE, verbose_name="Account"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name="Type",
    )
    transaction_date = models.DateField(verbose_name="Date of Transaction")
    description = models.TextField(null=True, blank=True, verbose_name="Narrations")

    def __str__(self):
        return f"{self.transaction_type.title()} of {self.amount} on {self.transaction_date}"
