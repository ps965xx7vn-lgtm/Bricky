import uuid
from django.db import models


class NewsletterSubscription(models.Model):
    """Model for storing newsletter subscriptions."""
    
    class StatusChoice(models.TextChoices):
        ACTIVE = "active", "Active"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    status = models.CharField(
        max_length=15,
        choices=StatusChoice.choices,
        default=StatusChoice.ACTIVE,
        db_index=True
    )
    subscribed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.email} - {self.status}"

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['subscribed_at']),
        ]
