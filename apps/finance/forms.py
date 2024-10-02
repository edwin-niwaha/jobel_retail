from django import forms
from django.forms import modelformset_factory
from .models import Transaction, ChartOfAccounts
from django.core.exceptions import ValidationError
import datetime


# =================================== ChartOfAccountsForm ===================================
class ChartOfAccountsForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        fields = ["account_name", "account_type", "account_number", "description"]
        widgets = {
            "account_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Name"}
            ),
            "account_type": forms.Select(attrs={"class": "form-control"}),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Number"}
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description (optional)",
                }
            ),
        }

    def clean_account_number(self):
        account_number = self.cleaned_data.get("account_number")
        if account_number and len(account_number) < 3:
            raise forms.ValidationError(
                "Account number must be at least 3 characters long."
            )
        return account_number

    def clean_account_name(self):
        account_name = self.cleaned_data.get("account_name")
        if account_name and len(account_name) < 3:
            raise forms.ValidationError(
                "Account name must be at least 3 characters long."
            )
        return account_name


# =================================== IncomeTransactionForm ===================================
class IncomeTransactionForm(forms.ModelForm):
    offset_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="asset"),
        required=True,  # Ensure an asset account is selected for double-entry
        label="Offset Account",
    )

    class Meta:
        model = Transaction
        fields = [
            "account",  # Income account (revenue)
            "amount",
            "transaction_date",
            "description",
            "offset_account",  # Offset account (e.g., Cash or Bank)
        ]
        widgets = {
            "account": forms.Select(
                attrs={
                    "class": "form-control",  # Bootstrap styling for the income account
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "min": "0",  # Ensure only positive values
                }
            ),
            "transaction_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",  # Use HTML5 date picker
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description (optional)",
                }
            ),
            "offset_account": forms.Select(
                attrs={
                    "class": "form-control",  # Bootstrap styling for offset account
                }
            ),
        }

        labels = {
            "account": "Income Account",
            "amount": "Transaction Amount",
            "transaction_date": "Transaction Date",
            "description": "Transaction Description",
            "offset_account": "Offset Account",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the queryset to revenue accounts for the income account field
        self.fields["account"].queryset = ChartOfAccounts.objects.filter(
            account_type="revenue"
        )

    def save(self, commit=True):
        """
        Override save method to set the transaction type to 'credit'
        for income transactions automatically and ensure double-entry.
        """
        # Call super to create the instance without saving to the DB
        instance = super().save(commit=False)

        # Ensure the transaction type is 'credit'
        instance.transaction_type = "credit"

        # Save the instance only if commit is True
        if commit:
            instance.save()

        return instance


# =================================== ExpenseTransactionForm ===================================
class ExpenseTransactionForm(forms.ModelForm):
    offset_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="asset"),
        required=True,  # Ensure an asset account is selected for double-entry
        label="Offset Account",
    )

    class Meta:
        model = Transaction
        fields = [
            "account",  # Expense account (expense)
            "amount",
            "transaction_date",
            "description",
            "offset_account",  # Offset account (e.g., Cash or Bank)
        ]
        widgets = {
            "account": forms.Select(
                attrs={
                    "class": "form-control",  # Bootstrap styling for the expense account
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "min": "0",  # Ensure only positive values
                }
            ),
            "transaction_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",  # Use HTML5 date picker
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description (optional)",
                }
            ),
            "offset_account": forms.Select(
                attrs={
                    "class": "form-control",  # Bootstrap styling for offset account
                }
            ),
        }

        labels = {
            "account": "Expense Account",
            "amount": "Transaction Amount",
            "transaction_date": "Transaction Date",
            "description": "Transaction Description",
            "offset_account": "Offset Account",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the queryset to expense accounts for the expense account field
        self.fields["account"].queryset = ChartOfAccounts.objects.filter(
            account_type="expense"
        )

    def save(self, commit=True):
        """
        Override save method to set the transaction type to 'debit'
        for expense transactions automatically and ensure double-entry.
        """
        # Call super to create the instance without saving to the DB
        instance = super().save(commit=False)

        # Ensure the transaction type is 'debit'
        instance.transaction_type = "debit"

        # Save the instance only if commit is True
        if commit:
            instance.save()

        return instance


# =================================== MultiJournalEntryForm ===================================
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "account",
            "offset_account",
            "amount",
            "transaction_type",
            "transaction_date",
            "description",
        ]
        widgets = {
            "account": forms.Select(
                attrs={"class": "form-control", "placeholder": "Select Account"}
            ),
            "offset_account": forms.Select(
                attrs={"class": "form-control", "placeholder": "Select Offset Account"}
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "step": "0.01",
                }
            ),
            "transaction_type": forms.Select(attrs={"class": "form-control"}),
            "transaction_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Narrations",
                }
            ),
        }


# Create the formset
from django.forms import modelformset_factory

TransactionFormSet = modelformset_factory(Transaction, form=TransactionForm, extra=1)
