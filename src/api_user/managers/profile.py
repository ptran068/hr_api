from uuid import UUID

from django.db import models
from rest_framework import serializers


class ProfileManager(models.Manager):
    def get_profile_by_id(self, id):
        try:
            return self.get(user__id=id)
        except:
            raise serializers.ValidationError('Profile not found')
