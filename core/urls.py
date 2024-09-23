# Import necessary modules and functions from Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Define the URL patterns for the project
urlpatterns = [
    # Admin route
    path("admin/", admin.site.urls),
    # Index/Home routes
    path("", include("apps.main.urls")),
    # Authentication routes
    path("auth/", include("apps.authentication.urls")),
    # Customer routes
    path("customers/", include("apps.customers.urls")),
    # Product routes
    path("products/", include("apps.products.urls")),
    path("inventory/", include("apps.inventory.urls")),
    # Sales routes
    path("sales/", include("apps.sales.urls")),
    # Orders routes
    path("orders/", include("apps.orders.urls")),
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
