import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ContactMessage(models.Model):
    """
    Model for storing contact form submissions
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


class NewsletterSubscription(models.Model):
    """
    Model for storing newsletter subscriptions
    """
    class StatusChoice(models.TextChoices):
        ACTIVE = "active", "Active"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    status = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.ACTIVE, db_index=True)
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


class HelpCategory(models.Model):
    """
    Model for Help/FAQ categories
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
    """
    Model for Help/FAQ articles
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


class Review(models.Model):
    """
    Model for product reviews
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    is_approved = models.BooleanField(default=True, db_index=True)
    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Review of {self.product.name} by {self.author.username}"

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['author']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['product', 'author']]  # One review per user per product
