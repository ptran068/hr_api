#!/usr/bin/env python

# author Huy
# date 9/17/2019

from django.db import models

from api_base.models import TimeStampedModel
from api_user.models import Profile
import uuid


def name_file(instance, filename):
    return '/'.join(['images', str(instance.profile.id), filename])


class Photo(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photo')
    photo = models.ImageField(upload_to=name_file, max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'hr_photos'
