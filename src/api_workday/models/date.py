#!/usr/bin/env python

# author Huy
# date 9/7/2019

from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import Profile
from api_workday.constants import Workday


class Date(TimeStampedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='date', default=1)
    date = models.DateField(null=True)
    title = models.CharField(max_length=255, null=True)
    content = models.CharField(max_length=255, default=None, null=True)
    reason = models.CharField(max_length=255, default=None, null=True)
    type = models.CharField(max_length=255, choices=Workday.TYPES, null=True, default=Workday.FULL)

    class Meta:
        db_table = "hr_date"
