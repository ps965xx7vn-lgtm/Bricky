"""Models for orders app.

Contains models for:
- Shopping cart management
- Order processing and tracking
- Customer information
- Delivery management
"""
import uuid
from decimal import Decimal
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from store.models import Product
from users.models import CustomUser


class Customer(models.Model):
    """Model representing a customer.
    
    Extends CustomUser with additional order-related
    information like phone and address.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
    )
    phone: Optional[str] = PhoneNumberField(blank=True)
    address: str = models.TextField(max_length=500,blank=True)

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class Order(models.Model):
    """Model representing an order.
    
    Tracks order lifecycle from creation to delivery
    with status management and timeline tracking.
    """
    class StatusChoice(models.TextChoices):
        NEW = "N", "New order"
        PROCESSED = "P", "Processed"
        SHIPPED = "S", "Shipped order"
        COMPLETED = "C", "Completed order"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    status = models.CharField(max_length=1, choices=StatusChoice.choices, db_index=True,
                              default=StatusChoice.NEW)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    address = models.TextField()
    is_draft = models.BooleanField(default=True)
    order_note = models.TextField(max_length=200, blank=True)
    registered_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(db_index=True, blank=True, null=True)
    delivered_at = models.DateTimeField(db_index=True, blank=True, null=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.customer.user.username} | {self.status}"

    def calculate_total(self):
        total = sum(item.total_price for item in self.order_items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total


class OrderElement(models.Model):
    """Model representing an item in an order.
    
    Stores individual product quantities and prices
    at the time of order placement.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="order_elements"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self) -> Decimal:
        price = self.price if self.price is not None else Decimal('0.00')
        quantity = self.quantity if self.quantity is not None else 0
        return price * quantity

    class Meta:
        verbose_name = 'Order Element'
        verbose_name_plural = 'Order Elements'


class Delivery(models.Model):
    """Model representing delivery information for an order.
    
    Manages delivery logistics including:
    - Delivery method and status
    - Tracking information
    - Recipient details
    - Delivery costs and insurance
    """
    class DeliveryMethod(models.TextChoices):
        STANDARD = "standard", "Standard Delivery (5-7 days)"
        EXPRESS = "express", "Express Delivery (2-3 days)"
        OVERNIGHT = "overnight", "Overnight Delivery (Next day)"
        PICKUP = "pickup", "In-Store Pickup"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In Transit"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Delivery Failed"
        RETURNED = "returned", "Returned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery"
    )
    method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.STANDARD
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True
    )
    tracking_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    delivery_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    estimated_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    delivery_address = models.TextField()
    delivery_notes = models.TextField(blank=True)
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_phone = PhoneNumberField(blank=True)
    signature_required = models.BooleanField(default=False)
    insurance = models.BooleanField(default=False)
    insurance_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Delivery for Order {self.order.id} - {self.get_status_display()}"

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['order']),
        ]


class Cart(models.Model):
    """Model representing a shopping cart for a user."""
    
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
        """Calculate total cart value."""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class CartItem(models.Model):
    """Model representing individual items in a cart."""
    
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
        """Calculate total price for this item."""
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
        ]
