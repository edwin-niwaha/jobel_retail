from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Volume, ProductVolume, Product, ProductImage
from apps.inventory.models import Inventory


# =================================== category form ===================================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter category name"}
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category description",
                }
            ),
        }
        labels = {
            "name": "Category Name",
            "description": "Description",
        }


# =================================== volume form ===================================
class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = ["ml"]
        widgets = {
            "ml": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "ml": "Volume in ML",
        }


# =================================== ProductVolumeForm form ===================================
class ProductVolumeForm(forms.ModelForm):
    MAX_IMAGE_SIZE_MB = 10

    class Meta:
        model = ProductVolume
        fields = ["volume", "cost", "price", "image"]
        widgets = {
            "volume": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)
        # Dynamically populate the volume choices
        self.fields["volume"].queryset = Volume.objects.all()

    def clean_volume(self):
        volume = self.cleaned_data.get("volume")
        # Check if a ProductVolume with the same product and volume already exists
        if (
            ProductVolume.objects.filter(product=self.product, volume=volume)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise ValidationError("Volume already assigned to this product.")
        return volume

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if image:
            image_size = image.size
            max_size = self.MAX_IMAGE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

            if image_size > max_size:
                raise forms.ValidationError(
                    f"Image size should not exceed {self.MAX_IMAGE_SIZE_MB} MB."
                )

        return image

    def save(self, commit=True):
        product_volume = super().save(commit=False)
        if self.product:
            product_volume.product = self.product
        if commit:
            product_volume.save()
        return product_volume


# =================================== Inventory form ===================================
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["quantity", "low_stock_threshold"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter stock quantity"}
            ),
            "low_stock_threshold": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter low stock threshold",
                }
            ),
        }
        labels = {
            "quantity": "Stock Quantity",
            "low_stock_threshold": "Low Stock Threshold",
        }


# =================================== product form ===================================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "status",
            "category",
            "product_type",
            "gender",
            "supplier",
        ]
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
            "product_type": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Product Name",
            "description": "Description",
            "status": "Status",
            "category": "Category",
            "product_type": "Product Type",
            "gender": "Gender",
            "suppliers": "Suppliers",  # Label for the suppliers field
        }


# =================================== CHILD PROFILE ===================================
class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = ProductImage
        fields = ["image"]

        labels = {
            "image": "Upload Product Image:",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget = forms.FileInput(attrs={"accept": "image/*"})

    def clean_image(self):
        image = self.cleaned_data.get("image")
        return image
