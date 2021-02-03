from api_user.models.profile import Profile
from rest_framework import serializers
from api_workday.models.remain_leave import RemainLeave


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'join_date']


class RemainLeaveSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = RemainLeave
        fields = '__all__'
        read_only_fields = ['profile']
