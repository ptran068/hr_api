#!/usr/bin/env python

# author Huy
# date 9/7/2019

from django.conf import settings
from rest_framework import serializers

from api_user.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'profile', 'photo')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(photo=f'{ret.get("photo")}')
        return ret
