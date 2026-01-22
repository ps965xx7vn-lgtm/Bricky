"""App configuration for notifications app."""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration for notifications application.
    
    Handles newsletter subscriptions and email notifications.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
