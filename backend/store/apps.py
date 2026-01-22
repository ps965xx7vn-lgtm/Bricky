"""App configuration for store app."""
from django.apps import AppConfig


class StoreConfig(AppConfig):
    """Configuration for store application.
    
    Handles product catalog, categories, search, and reviews.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
