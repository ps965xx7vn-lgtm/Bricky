"""App configuration for core app."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for core application.
    
    Handles contact forms, legal pages, and help/FAQ system.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
