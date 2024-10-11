from django.contrib import admin

# Register your models here.
from .models import Sale, SaleDetail

admin.site.register(Sale)
admin.site.register(SaleDetail)
