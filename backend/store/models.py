"""Models for store app.

Contains models for:
- Product catalog with categories
- Product reviews and ratings
"""
import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from users.models import CustomUser

class Category(models.Model):
    """Model representing a product category.
    
    Categories organize products and include images
    for visual representation in the catalog.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(blank=True, upload_to="categories", default="user_pictures/default.png")
    title: str= models.CharField(max_length=200,unique=True,db_index=True)
    slug:str= models.SlugField(unique=True,db_index=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["title"])
        ]
class Product(models.Model):
    """Model representing a product.
    
    Contains product information including:
    - Basic details (name, description, price)
    - Stock management
    - Status (new, old, coming soon)
    - Category relationship
    """
    class StatusChoice(models.TextChoices):
        NEW = "N", "New product"
        OLD = "O", "Old product"
        COMMING_SOON = "C", "Comming soon product"

    status = models.CharField(max_length=1, choices=StatusChoice.choices, db_index=True,
                              default=StatusChoice.NEW)
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=255, db_index=True)
    slug: str = models.SlugField(unique=True, db_index=True)
    description: str = models.TextField(blank=True)
    picture = models.ImageField(blank=True, upload_to="products", default="products/default.png")
    price: float = models.DecimalField(max_digits=10, decimal_places=2)
    stock: int = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    is_active: bool = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ['-created_at']


class Review(models.Model):
    """
    Model for product reviews.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
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
        unique_together = [['product', 'author']]

