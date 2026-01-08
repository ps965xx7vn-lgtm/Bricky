"""
Django signals for orders app
Automatically creates Customer profile when a new user is created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import Customer


@receiver(post_save, sender=CustomUser)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Customer profile when a new CustomUser is created
    """
    if created:
        Customer.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_customer_profile(sender, instance, **kwargs):
    """
    Signal to ensure Customer profile exists (handles edge cases)
    """
    if hasattr(instance, 'customer'):
        instance.customer.save()
