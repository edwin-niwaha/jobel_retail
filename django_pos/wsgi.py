"""
WSGI config for django_pos project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()


if os.environ.get("DJANGO_ENV") == "development":
    settings = "django_pos.settings_dev"
else:
    settings = "django_pos.settings"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)


application = get_wsgi_application()
