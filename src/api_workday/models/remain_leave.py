from django.db import models
import uuid
from api_base.models import TimeStampedModel
from api_user.models.profile import Profile
import datetime
from api_workday.managers.remain_leave import RemainLeaveManager


class RemainLeave(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    year = models.IntegerField(default=datetime.datetime.now().year)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    bonus = models.FloatField(default=0)
    annual_leave = models.FloatField(default=0)
    annual_leave_last_year = models.FloatField(default=0)
    current_days_off = models.FloatField(default=0)

    objects = RemainLeaveManager()

    class Meta:
        db_table = 'hr_remain_year'
