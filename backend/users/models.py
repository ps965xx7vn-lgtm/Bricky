"""Models for users app.

Contains custom user model extending Django's AbstractUser
with additional fields for profile management.
"""
import uuid
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    """Custom user model.
    
    Extends Django's AbstractUser with:
    - UUID primary key
    - Email verification system
    - Profile picture
    - Phone number
    - Telegram ID for bot integration
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email: str = models.EmailField(unique=True, )
    email_is_verified: bool = models.BooleanField(default=False)
    picture = models.ImageField(blank=True,upload_to="user_pictures", default="user_pictures/default.png")
    phone: Optional[str] = PhoneNumberField(blank=True)
    tg_id: int = models.IntegerField(blank=True,null=True)


    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name="User"
        verbose_name_plural="Users"
        indexes=[
            models.Index(fields=["email"])
        ]

