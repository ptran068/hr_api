from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User
import uuid

class UserEducation(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    school = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=255)
    graduated_year = models.IntegerField(null=True)
    additional_notes = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_education")

    class Meta:
        db_table = 'hr_user_education'

