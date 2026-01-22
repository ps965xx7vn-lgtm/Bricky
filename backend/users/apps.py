"""App configuration for users app."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for users application.
    
    Handles user authentication, profiles, and email verification.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
