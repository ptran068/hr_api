from django.db import models
from rest_framework import serializers
import datetime


class RemainLeaveManager(models.Manager):
    def get_remain_leave_by_profile_id(self, id):
        remain_leave = self.filter(profile_id=id, year=datetime.datetime.now().year).first()
        if remain_leave is None:
            raise serializers.ValidationError({'status': 'Data not found'})
        return remain_leave

    def get_remain_leave_next_year_by_profile_id(self, id):
        remain_leave = self.filter(profile_id=id, year=datetime.datetime.now().year+1).first()
        if remain_leave is None:
            raise serializers.ValidationError({'status': 'Data not found'})
        return remain_leave

    def get_remain_leave_last_year_by_profile_id(self, id):
        remain_leave = self.filter(profile_id=id, year=datetime.datetime.now().year-1).first()
        if remain_leave is None:
            raise serializers.ValidationError({'status': 'Data not found'})
        return remain_leave


