"""App configuration for orders app."""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for orders application.
    
    Handles shopping cart, checkout, order processing, and delivery.
    Registers signals for automatic Customer profile creation.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    
    def ready(self):
        """Import signals when app is ready."""
        import orders.signals