from rest_framework import serializers

from api_user.models.titles import Titles
from api_user.models import User
from api_user.serializers import ProfileSerializers


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializers(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'profile', 'active', 'admin', 'title', 'staff')


class TitlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Titles
        fields = '__all__'

    def create(self, validate_data):
        return Titles.objects.create(**validate_data)