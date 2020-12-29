from django.db import models
import uuid

# Create your models here.

class Provider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    budget = models.CharField(max_length=20)
    has_vegetarian = models.BooleanField(default=False)
    description = models.TextField(max_length=255, null=True, blank=True)
    address = models.TextField(max_length=255)
    link = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
