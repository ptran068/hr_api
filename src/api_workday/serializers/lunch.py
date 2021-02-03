#!/usr/bin/env python

# author Huy 
# date 10/23/2019

from rest_framework import serializers

from api_workday.models import Lunch, Lunchdate


class LunchSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['start'] = ret['end'] = Lunchdate.objects.get(id=ret.get('date')).date
        return ret

    class Meta:
        model = Lunch
        fields = ('id', 'profile', 'date')
