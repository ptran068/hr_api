from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import re

from api_user.models import User


class InviteListSerializer(serializers.Serializer):
    def validate(self, attrs):
        email = attrs.get('email')
        name = attrs.get('name')
        email_regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        if not (re.search(email_regex, email)):
            return {
                'email': email,
                'name': name,
                'status': 'Invalid email format',
                'success': False
            }
        existed = User.objects.filter(email=email).count()
        if existed:
            return {
                'email': email,
                'name': name,
                'status': 'Already existed',
                'success': False
            }
        return {
                'email': email,
                'name': name,
                'status': 'Success',
                'success': True
            }

    name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
