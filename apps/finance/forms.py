from django import forms
from .models import Transaction, ChartOfAccounts
from django.core.exceptions import ValidationError
import datetime


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


class MultiJournalEntryForm(forms.Form):
    entries = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )  # To handle dynamic entries

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry_forms = self.create_entry_forms()

    def create_entry_forms(self, num_entries=3):  # Set default for initial forms
        forms_list = []
        for i in range(num_entries):
            forms_list.append(self.create_entry_form(i))
        return forms_list

    def create_entry_form(self, index):
        return {
            f"account_{index}": forms.ModelChoiceField(
                queryset=ChartOfAccounts.objects.all(),
                label=f"Account {index + 1}",
                widget=forms.Select(attrs={"class": "form-control"}),
            ),
            f"amount_{index}": forms.DecimalField(
                label=f"Amount {index + 1}",
                min_value=0,
                widget=forms.NumberInput(
                    attrs={"class": "form-control", "placeholder": "Enter amount"}
                ),
            ),
            f"transaction_date_{index}": forms.DateField(
                label=f"Transaction Date {index + 1}",
                widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            ),
            f"description_{index}": forms.CharField(
                label=f"Description {index + 1}",
                required=False,
                widget=forms.Textarea(
                    attrs={
                        "class": "form-control",
                        "rows": 2,
                        "placeholder": "Enter description",
                    }
                ),
            ),
            f"transaction_type_{index}": forms.ChoiceField(
                choices=[("debit", "Debit"), ("credit", "Credit")],
                label=f"Transaction Type {index + 1}",
                widget=forms.Select(attrs={"class": "form-control"}),
            ),
        }

    def clean_entries(self):
        # Validate each entry form
        entries = []
        for i in range(len(self.entry_forms)):
            entry_data = {
                field: self.cleaned_data.get(f"{field}_{i}")
                for field in [
                    "account",
                    "amount",
                    "transaction_date",
                    "description",
                    "transaction_type",
                ]
            }

            if entry_data["amount"] <= 0:
                raise forms.ValidationError(
                    f"Amount for entry {i + 1} must be greater than zero."
                )

            entries.append(entry_data)
        return entries

    def save(self, commit=True):
        entries = self.cleaned_data["entries"]
        transactions = []
        for entry in entries:
            transaction = Transaction(
                paying_account=(
                    entry["account"] if entry["transaction_type"] == "debit" else None
                ),
                receiving_account=(
                    entry["account"] if entry["transaction_type"] == "credit" else None
                ),
                amount=entry["amount"],
                transaction_date=entry["transaction_date"],
                description=entry["description"],
                transaction_type=entry["transaction_type"],
            )
            if commit:
                transaction.save()
            transactions.append(transaction)
        return transactions


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
