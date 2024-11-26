from django import forms
from django.forms import modelformset_factory
from .models import Transaction, ChartOfAccounts


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


# =================================== ImportCOAForm ===================================
class ImportCOAForm(forms.Form):
    excel_file = forms.FileField()
    excel_file.widget.attrs["class"] = "form-control-file"


# =================================== IncomeTransactionForm ===================================
class IncomeTransactionForm(forms.ModelForm):
    paying_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="asset"),
        label="Paying Account",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    receiving_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="revenue"),
        label="Income Account",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Transaction Amount",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",  # Bootstrap class
                "placeholder": "Enter amount",
            }
        ),
    )
    transaction_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",  # Bootstrap class
                "type": "date",  # HTML5 date input
            }
        ),
        label="Date of Transaction",
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",  # Bootstrap class
                "rows": 3,
                "placeholder": "Optional description",
            }
        ),
        label="Transaction Description",
        required=False,
    )

    class Meta:
        model = Transaction
        fields = [
            "paying_account",
            "receiving_account",
            "amount",
            "transaction_date",
            "description",
        ]

    def save(self, commit=True):
        # Create the first transaction entry (receiving account)
        receiving_transaction = super().save(commit=False)
        receiving_transaction.account = self.cleaned_data["receiving_account"]
        receiving_transaction.transaction_type = "credit"  # Automatically set to credit

        if commit:
            receiving_transaction.save()

        # Create the second transaction entry (paying account)
        paying_transaction = Transaction(
            account=self.cleaned_data["paying_account"],
            amount=self.cleaned_data["amount"],
            transaction_type="debit",  # Automatically set to debit
            transaction_date=self.cleaned_data["transaction_date"],
            description=self.cleaned_data["description"],
        )

        if commit:
            paying_transaction.save()

        return receiving_transaction


# =================================== ExpenseTransactionForm ===================================
class ExpenseTransactionForm(forms.ModelForm):
    receiving_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="asset"),
        label="Receiving Account",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    paying_account = forms.ModelChoiceField(
        queryset=ChartOfAccounts.objects.filter(account_type="expense"),
        label="Expense Account",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Transaction Amount",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",  # Bootstrap class
                "placeholder": "Enter amount",
            }
        ),
    )
    transaction_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",  # Bootstrap class
                "type": "date",  # HTML5 date input
            }
        ),
        label="Date of Transaction",
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",  # Bootstrap class
                "rows": 3,
                "placeholder": "Optional description",
            }
        ),
        label="Transaction Description",
        required=False,
    )

    class Meta:
        model = Transaction
        fields = [
            "paying_account",
            "receiving_account",
            "amount",
            "transaction_date",
            "description",
        ]

    def save(self, commit=True):
        # Create the first transaction entry (paying account)
        paying_transaction = super().save(commit=False)
        paying_transaction.account = self.cleaned_data["paying_account"]
        paying_transaction.transaction_type = "debit"  # Automatically set to debit

        if commit:
            paying_transaction.save()

        # Create the second transaction entry (receiving account)
        receiving_transaction = Transaction(
            account=self.cleaned_data["receiving_account"],
            amount=self.cleaned_data["amount"],
            transaction_type="credit",  # Automatically set to credit
            transaction_date=self.cleaned_data["transaction_date"],
            description=self.cleaned_data["description"],
        )

        if commit:
            receiving_transaction.save()

        return paying_transaction


# =================================== MultiJournalEntryForm ===================================
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "account",
            "amount",
            "transaction_type",  # Debit or Credit
            # "transaction_date",
            "description",
        ]
        widgets = {
            "account": forms.Select(
                attrs={"class": "form-control", "placeholder": "Select Account"}
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "step": "0.01",
                }
            ),
            "transaction_type": forms.Select(
                attrs={"class": "form-control"}
            ),  # Ensure this field is included
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Narrations"}
            ),
        }


TransactionFormSet = modelformset_factory(Transaction, form=TransactionForm, extra=2)
