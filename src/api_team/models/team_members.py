from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import User
from api_team.models import Team


class TeamMembers(TimeStampedModel):
    member = models.ForeignKey(User, related_name="member", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name="team", on_delete=models.CASCADE)

    class Meta:
        db_table = 'hr_team_members'

