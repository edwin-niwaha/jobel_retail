# Import necessary modules and functions from Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

# Define the URL patterns for the project
urlpatterns = [
    # Admin route
    path("admin/", admin.site.urls),
    # Main application routes
    path("", include("apps.main.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/customers/", include("apps.customers.urls")),
    path("api/supplier/", include("apps.supplier.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/sales/", include("apps.sales.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/finance/", include("apps.finance.urls")),
    # Social Authentication
    re_path(r"^oauth/", include("social_django.urls", namespace="social")),
    # Djoser authentication routes
]

# Additional URL patterns for debugging and media files in development mode
if settings.DEBUG:
    urlpatterns += [
        # Reload routes for browser refresh during development
        path("__reload__/", include("django_browser_reload.urls")),
        # Debug toolbar routes for debugging purposes
        path("__debug__/", include("debug_toolbar.urls")),
    ]

    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
