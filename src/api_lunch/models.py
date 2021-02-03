from django.db import models
import uuid
from django.utils import timezone
from api_providers.models import Provider


class Lunch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    has_veggie = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True, max_length=255)
    date = models.DateField(null=True, default=timezone.now)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.provider

    
