"""Models for core app.

Contains models for:
- Contact messages from visitors
- Help/FAQ system with categories and articles
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ContactMessage(models.Model):
    """Model for storing contact form submissions.
    
    Stores messages from visitors with subject categorization,
    status tracking, and reply functionality.
    """
    class SubjectChoice(models.TextChoices):
        GENERAL = "general", "General Inquiry"
        ORDER = "order", "Order Question"
        SHIPPING = "shipping", "Shipping Issue"
        RETURN = "return", "Return/Refund"
        PARTNERSHIP = "partnership", "Partnership Opportunity"
        OTHER = "other", "Other"

    class StatusChoice(models.TextChoices):
        NEW = "new", "New"
        READING = "reading", "Reading"
        REPLIED = "replied", "Replied"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=20, choices=SubjectChoice.choices, db_index=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoice.choices, default=StatusChoice.NEW, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class HelpCategory(models.Model):
    """Model for Help/FAQ categories.
    
    Organizes help articles into logical categories
    with icons and custom ordering.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-question-circle', help_text='Font Awesome icon class')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Help Category'
        verbose_name_plural = 'Help Categories'
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]


class HelpArticle(models.Model):
    """Model for Help/FAQ articles.
    
    Individual help articles within categories.
    Tracks views and helpfulness feedback.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.category.title} - {self.title}"

    class Meta:
        verbose_name = 'Help Article'
        verbose_name_plural = 'Help Articles'
        ordering = ['category', 'order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
        ]
