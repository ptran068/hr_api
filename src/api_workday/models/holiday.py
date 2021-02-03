import uuid
from datetime import datetime

from django.db import models

from api_base.models import TimeStampedModel


class Holiday(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField(null=True)
    descriptions = models.TextField(null=True)

    class Meta:
        db_table = 'hr_holidays'
