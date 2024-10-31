from django import forms
from .models import PAYMENT_METHOD_CHOICES, ORDER_STATUS_CHOICES, Order


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First Name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last Name (optional)",
            }
        ),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email (optional)",
            }
        ),
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone Number",
            }
        ),
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Address",
                "rows": 2,  # Making it a multi-line input
            }
        ),
    )


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_status(self):
        status = self.cleaned_data.get("status")
        order = self.instance

        if order.status == status:
            raise forms.ValidationError(
                "The selected status is already set for this order."
            )

        return status
