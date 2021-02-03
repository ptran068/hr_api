from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User


class Team(TimeStampedModel):
    team_name = models.CharField(max_length=255, unique=True)
    team_email = models.EmailField(max_length=255, blank=True, null=True)
    team_leader = models.OneToOneField(User, related_name='leader', on_delete=models.SET_NULL, blank=True, null=True)
    project_manager = models.ForeignKey(User, related_name='pm', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'hr_teams'

