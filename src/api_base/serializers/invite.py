from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_user.models import User


class InviteSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        existed = User.objects.filter(email=attrs.get('email')).count()
        if not existed:
            raise ValidationError("Email is not available")
        return True

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
