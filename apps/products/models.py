from django.db import models
from django.forms import model_to_dict
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from apps.supplier.models import Supplier
from cloudinary.models import CloudinaryField

# Define choices for product status
STATUS_CHOICES = [
    ("", "-- Choose status --"),
    ("ACTIVE", "Active"),
    ("INACTIVE", "Inactive"),
]

# Define choices for gender
GENDER_CHOICES = [
    ("", "-- Choose gender --"),
    ("Unisex", "Unisex"),
    ("Male", "Male"),
    ("Female", "Female"),
]

# Define choices for product type
PRODUCT_TYPE_CHOICES = [
    ("", "-- Choose product type --"),
    ("Roll-On", "Roll-On"),
    ("Spray", "Spray"),
]


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
    )
    description = models.CharField(
        max_length=100, blank=True, verbose_name="Description"
    )

    class Meta:
        db_table = "category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Volume(models.Model):
    ml = models.IntegerField(unique=True, verbose_name="Volume in ML")

    def __str__(self):
        return f"{self.ml} ML"


class Product(models.Model):
    name = models.CharField(max_length=256, verbose_name="Product Name")
    description = models.TextField(verbose_name="Product Description")
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=10, verbose_name="Status"
    )
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Category",
    )
    volumes = models.ManyToManyField(
        Volume, through="ProductVolume", related_name="products"
    )
    supplier = models.ForeignKey(
        Supplier,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Supplier",
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=10,
        default="Unisex",
        verbose_name="Targeted Gender",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "product"

    def __str__(self):
        return self.name

    def to_json(self):
        item = model_to_dict(self)
        item.update(
            {
                "id": self.id,
                "text": self.name,
                "category": self.category.name if self.category else None,
                "quantity": (
                    self.inventory.quantity if hasattr(self, "inventory") else 0
                ),
                "total_product": 0,
            }
        )
        return item

    @property
    def prefixed_id(self):
        return f"JBL{self.pk:03d}"


class ProductVolume(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_type = models.CharField(
        choices=PRODUCT_TYPE_CHOICES,
        max_length=10,
        default="Spray",
        verbose_name="Type",
    )
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)

    # Cost and Price determined by the selected volume for this product
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Cost Price"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Selling Price"
    )
    # image = models.ImageField(
    #     upload_to="product_volume_images/",
    #     validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    #     verbose_name="Product Volume Image",
    #     null=True,
    #     blank=True,
    # )
    image = CloudinaryField(
        "product_volume_image",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("product", "volume", "product_type")
        verbose_name = "Product Volume"
        verbose_name_plural = "Product Volumes"

    def __str__(self):
        return f"{self.product.name} - {self.volume.ml}ML (Cost: {self.cost}, Price: {self.price})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    # image = models.ImageField(upload_to="product_images/", verbose_name="Product Image")
    image = CloudinaryField("image", blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name="Is Default")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        db_table = "product_image"
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Image for {self.product.name} (Default: {self.is_default})"

    def clean(self):
        # Ensure only one default image is set per product
        if self.is_default:
            default_image_exists = (
                ProductImage.objects.filter(product=self.product, is_default=True)
                .exclude(id=self.id)
                .exists()
            )

            if default_image_exists:
                raise ValidationError("Only one default image can be set per product.")

    def save(self, *args, **kwargs):
        # Ensure no other images are marked as default if this one is set as default
        if self.is_default:
            ProductImage.objects.filter(product=self.product, is_default=True).update(
                is_default=False
            )

        super().save(*args, **kwargs)
