import uuid

from django.db import models
from decimal import Decimal
from users.models import CustomUser

class Category(models.Model):
    """
    Model representing a product category
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


class Cart(models.Model):
    """
    Model representing a shopping cart for a user
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart for {self.user.username}"

    def get_total_price(self) -> Decimal:
        """Calculate total cart value"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class CartItem(models.Model):
    """
    Model representing individual items in a cart
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity: int = models.PositiveIntegerField(default=1)
    price: Decimal = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self) -> Decimal:
        """Calculate total price for this item"""
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
        ]

