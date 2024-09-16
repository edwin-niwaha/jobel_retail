from django import forms
from .models import Order, ORDER_STATUS_CHOICES, PAYMENT_METHOD_CHOICES


class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect
    )


# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ["shipping_address", "payment_method"]
#         widgets = {
#             "shipping_address": forms.Textarea(attrs={"class": "form-control"}),
#             "payment_method": forms.Select(attrs={"class": "form-control"}),
#         }
#         labels = {
#             "shipping_address": "Shipping Address",
#             "payment_method": "Payment Method",
#         }
#         help_texts = {
#             "shipping_address": "Please provide your shipping address.",
#             "payment_method": "Please select your preferred payment method.",
#         }
#         error_messages = {
#             "shipping_address": {"required": "Please enter your shipping address."},
#             "payment_method": {
#                 "required": "Please select your preferred payment method."
#             },
#         }
