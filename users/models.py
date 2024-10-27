from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),  # Índice en el campo is_active
        ]

class Entry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
