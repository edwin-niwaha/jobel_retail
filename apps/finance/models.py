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
TRANSACTION_TYPE_CHOICES = [
    ("debit", "Debit"),
    ("credit", "Credit"),
]


# class Transaction(models.Model):
#     account = models.ForeignKey(
#         "ChartOfAccounts", on_delete=models.CASCADE, related_name="transactions"
#     )
#     offset_account = models.ForeignKey(
#         "ChartOfAccounts", on_delete=models.CASCADE, related_name="offset_transactions"
#     )
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
#     transaction_date = models.DateField()
#     description = models.TextField(blank=True, null=True)

#     class Meta:
#         ordering = ["transaction_date"]
#         db_table = "transactions"
#         verbose_name = "Transaction"
#         verbose_name_plural = "Transactions"

#     def __str__(self):
#         return f"{self.account} - {self.get_transaction_type_display()} {self.amount} on {self.transaction_date}"

#     def clean(self):
#         if self.amount <= 0:
#             raise ValidationError("Transaction amount must be positive.")

#     def save(self, *args, **kwargs):
#         """
#         Override save to ensure double-entry accounting.
#         Creates both the debit and credit entries, but only once.
#         """
#         # Use a flag to prevent creating an infinite loop of offset transactions
#         if not getattr(self, "_is_offset", False):
#             # Create the corresponding offset transaction
#             self.create_offset_transaction()

#         super().save(*args, **kwargs)

#     def create_offset_transaction(self):
#         """
#         Create the opposite transaction (credit for debit, and vice versa) to maintain double-entry accounting.
#         """
#         # Determine the opposite transaction type
#         offset_transaction_type = (
#             "credit" if self.transaction_type == "debit" else "debit"
#         )

#         # Create the offset transaction and mark it as an offset transaction
#         offset_transaction = Transaction(
#             account=self.offset_account,
#             offset_account=self.account,  # Swap the accounts for double-entry
#             amount=self.amount,
#             transaction_type=offset_transaction_type,
#             transaction_date=self.transaction_date,
#             description=f"Offset for {self.get_transaction_type_display()} transaction",
#         )

#         # Set a flag to prevent recursion
#         offset_transaction._is_offset = True

#         # Save the offset transaction
#         offset_transaction.save()


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
