from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ValidationError


def validate_youtube_url(value):
    """Validator to ensure the provided URL is a valid YouTube video link."""
    parsed_url = urlparse(value)
    if parsed_url.netloc not in ["www.youtube.com", "youtube.com"]:
        raise ValidationError("Please provide a valid YouTube URL.")
    if not parse_qs(parsed_url.query).get("v"):
        raise ValidationError("Invalid YouTube URL. Ensure it contains a video ID.")
