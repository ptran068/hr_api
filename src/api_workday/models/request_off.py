import uuid

from django.db import models

from api_base.models import TimeStampedModel
from api_user.models.profile import Profile
from api_workday.models.type_off import TypeOff


class RequestOff(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=255, default='Pending')
    reason = models.CharField(max_length=255, null=True, blank=True)
    type_off = models.ForeignKey(TypeOff, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'hr_request_off'
