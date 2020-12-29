from rest_framework import serializers
from .models import UserLunch
from api_lunch.models import Lunch
from api_user.models import Profile


class LunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lunch
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserLunchSerializer(serializers.ModelSerializer):
    lunch = LunchSerializer(many=False)
    profile = ProfileSerializer(many=False)
    class Meta:
        model = UserLunch
        fields = '__all__'


class CreateUserLunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLunch
        fields = '__all__'
