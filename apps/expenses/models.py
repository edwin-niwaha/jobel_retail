from django.db import models
from django.utils import timezone


class OperationalExpense(models.Model):
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Expense on {self.date} - {self.description}"
