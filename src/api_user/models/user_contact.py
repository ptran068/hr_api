from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User
import uuid

class UserContact(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    permanent_address = models.CharField(max_length=100)
    temporary_address = models.CharField(max_length=100, null=True)
    household_registration_number = models.CharField(max_length=50, null=True)
    contact_emergency = models.CharField(max_length=11, null=True, validators=[
        RegexValidator(regex=r'^\d+$', message='A valid integer is required.'),
        MinLengthValidator(9)])
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_contact")

    class Meta:
        db_table = 'hr_user_contact'

