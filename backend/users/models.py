import uuid
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    """
    Manager for custom model user
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email: str = models.EmailField(unique=True, )
    email_is_verified: bool = models.BooleanField(default=False)
    picture = models.ImageField(blank=True,upload_to="user_pictures", default="user_pictures/default.png")
    phone: Optional[str] = PhoneNumberField(blank=True)

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name="User"
        verbose_name_plural="Users"
        indexes=[
            models.Index(fields=["email"])
        ]
