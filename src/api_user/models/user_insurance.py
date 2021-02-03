from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User
import uuid

class UserInsurance(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    social_insurance_code = models.CharField(max_length=50)
    start_date = models.DateField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_insurance")

    class Meta:
        db_table = 'hr_user_insurance'

