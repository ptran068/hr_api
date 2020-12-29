from django.db import models
from django.db.models import Manager
from django.utils import timezone


class TimeStampedModel(models.Model):
    objects = Manager
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
