from django.db import models
import uuid
from django.utils import timezone
from api_user.models import Profile
from api_lunch.models import Lunch


class UserLunch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField(null=True, default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    lunch = models.ForeignKey(Lunch, blank=True, null=True, on_delete=models.CASCADE)
    has_veggie = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.date
        
    class Meta:
        ordering = ['-created_at']
