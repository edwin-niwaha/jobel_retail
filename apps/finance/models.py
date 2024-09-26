from django.core.exceptions import ValidationError
from django.db import models


# =================================== ChartOfAccounts ===================================
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


# =================================== Transaction ===================================
class Transaction(models.Model):
    ACCOUNT_ROLE_CHOICES = [
        ("paying", "Paying Account"),
        ("receiving", "Receiving Account"),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ("debit", "Debit"),
        ("credit", "Credit"),
    ]

    account = models.ForeignKey(
        ChartOfAccounts, on_delete=models.CASCADE, verbose_name="Account"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Transaction Amount"
    )
    transaction_type = models.CharField(
        max_length=6, choices=TRANSACTION_TYPE_CHOICES, verbose_name="Transaction Type"
    )
    transaction_date = models.DateField(verbose_name="Transaction Date")
    description = models.TextField(
        blank=True, null=True, verbose_name="Transaction Description"
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["transaction_date"]
        db_table = "transactions"

    def __str__(self):
        return f"{self.account} - {self.transaction_type.capitalize()} {self.amount} on {self.transaction_date}"

    def clean(self):
        # Ensure the amount is positive
        if self.amount <= 0:
            raise ValidationError("Transaction amount must be positive.")

        # Ensure debit transactions align with paying accounts and credit with receiving accounts
        if self.transaction_type == "debit" and self.account.account_role != "paying":
            raise ValidationError(
                "Debit transactions must be associated with a paying account."
            )
        if (
            self.transaction_type == "credit"
            and self.account.account_role != "receiving"
        ):
            raise ValidationError(
                "Credit transactions must be associated with a receiving account."
            )

    def save(self, *args, **kwargs):
        # Run the clean method before saving
        self.clean()
        super().save(*args, **kwargs)
