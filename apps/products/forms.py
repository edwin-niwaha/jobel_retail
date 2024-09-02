from django import forms
from .models import Category, Product


# =================================== category form ===================================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter category name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter category description",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Category Name",
            "description": "Category Description",
            "status": "Category Status",
        }


# =================================== product model ===================================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "status",
            "category",
            "price",
        ]  # Include all fields from the model

        # Custom widgets and attributes for form fields can be added here
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter product name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product description",
                    "rows": 3,
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter price"}
            ),
        }

        # Custom labels can be added here if needed
        labels = {
            "name": "Product Name",
            "description": "Description",
            "status": "Status",
            "category": "Category",
            "price": "Price",
        }
