from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User
import uuid

class UserIdentity(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    identity_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^\d+$', message='A valid integer is required.'),
        MinLengthValidator(9)])
    issue_date = models.DateField()
    issue_place = models.CharField(max_length=100)
    place_of_birth  = models.CharField(max_length=100, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_identity")

    class Meta:
        db_table = 'hr_user_identity'

