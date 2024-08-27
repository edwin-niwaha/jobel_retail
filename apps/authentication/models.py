from django.contrib.auth.models import User
from django.db import models
from PIL import Image


# =================================== Profile Model  ===================================
class Profile(models.Model):
    ROLE_CHOICES = (
        ("administrator", "Administrator"),
        ("manager", "Manager"),
        ("staff", "Staff"),
        ("guest", "Guest"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="guest")
    avatar = models.ImageField(default="default.jpg", upload_to="profile_images")
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)


# =================================== Contact Model  ===================================
class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Your Name")
    email = models.EmailField(verbose_name="Your Email")
    message = models.TextField(verbose_name="Message")
    is_valid = models.BooleanField(default=False, verbose_name="Valid?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "User Feedback"
        db_table = "user_feedback"

    def __str__(self):
        return f"Feedback from {self.name} ({self.email})"
