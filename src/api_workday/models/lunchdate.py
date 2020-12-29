#!/usr/bin/env python

# author Huy
# date 11/4/2019

from django.db import models
from django.utils import timezone

from api_base.models import TimeStampedModel


class Lunchdate(TimeStampedModel):
    date = models.DateField(null=True, default=timezone.now)
    veggie = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_lunchdate'
