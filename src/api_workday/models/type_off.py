import uuid

from django.db import models

from api_base.models import TimeStampedModel
from api_workday.constants import Workday


class TypeOff(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, null=True)
    type = models.IntegerField(choices=Workday.TYPE_LEAVES, default=0)
    is_ot_days = models.IntegerField(choices=Workday.OT_DAYS, default=0)
    is_paid_salary = models.BooleanField(default=True, blank=True)
    descriptions = models.TextField()
    add_sub_day_off = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_type_off'
