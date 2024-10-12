from django.urls import path, include
from .views import LogoutView

urlpatterns = [
    path("", include("djoser.urls")),  # Djoser default URLs
    path("", include("djoser.urls.jwt")),  # Djoser JWT URLs
    path("logout/", LogoutView.as_view()),  # Custom logout URL
]
