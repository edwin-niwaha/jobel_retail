import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")

# DEBUG = os.environ.get("DEBUG", False)
# Production
DEBUG = False

# Development
# DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'jobelstore.up.railway.app']

CSRF_TRUSTED_ORIGINS = ['https://jobelstore.up.railway.app']

# Application definition
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "djoser",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "social_django",
    "bootstrap5",
    "formtools",
    "crispy_forms",
    "crispy_bootstrap5",
    "django.contrib.humanize",
    # Custom apps
    "apps.main",
    "apps.authentication",
    "apps.supplier",
    "apps.products",
    "apps.inventory",
    "apps.customers",
    "apps.orders",
    "apps.sales",
    "apps.finance",
]

# Middleware configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # For handling CORS
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",  # Handles social auth exceptions
]

# CORS allowed origins
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# URL routing
ROOT_URLCONF = "core.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Add custom template directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Default context processors
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Social authentication context processors
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                # Custom context processors
                "apps.authentication.context_processors.guest_profiles_context",
                "apps.authentication.context_processors.guest_user_feedback_context",
                "apps.authentication.context_processors.low_stock_alerts_context",
                "apps.authentication.context_processors.pending_orders_context",
            ],
        },
    },
]

# WSGI configuration
WSGI_APPLICATION = "core.wsgi.application"

# Database configuration (PostgreSQL) Local host
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("DB_NAME", "default_db_name"),
#         "USER": os.environ.get("DB_USER", "default_user"),
#         "PASSWORD": os.environ.get("DB_PASSWORD", "default_password"),
#         "HOST": os.environ.get("DB_HOST", "localhost"),
#         "PORT": os.environ.get("DB_PORT", "5432"),
#     }
# }


# Database configuration (PostgreSQL) Online
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            None  # Use DATABASE_URL if provided
        )
    )
}

# Fallback to manual configuration if DATABASE_URL is not set
if not DATABASES["default"]:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "default_db_name"),
        "USER": os.getenv("DB_USER", "default_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "default_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }



# Django REST framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        # Uncomment for JWT support:
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# Simple JWT configuration
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Email backend (console for development)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Djoser configuration
DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "auth/password/reset-password-confirmation/?uid={uid}&token={token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": False,
    "SERIALIZERS": {},
}

# General site settings
SITE_NAME = "Test Django Next.js"
DOMAIN = "localhost:3000"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",  # Default backend
)

# Localization and time zone settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static and media files configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # Additional static files directory

STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Login and session settings
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "login"

SESSION_COOKIE_AGE = 3600  # 60 * 60 seconds = 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Close session when browser closes

# Social authentication keys (from environment variables)
SOCIAL_AUTH_GITHUB_KEY = os.getenv("GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("GITHUB_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_SECRET")

# Load your MTN credentials from the .env file
MTN_CLIENT_ID = os.getenv("MTN_CLIENT_ID")
MTN_CLIENT_SECRET = os.getenv("MTN_CLIENT_SECRET")
MTN_SUBSCRIPTION_KEY = os.getenv("MTN_SUBSCRIPTION_KEY")


# Email configuration (for production)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = os.getenv("EMAIL_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Crispy Forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Logging configuration
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
