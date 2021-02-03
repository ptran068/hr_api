from rest_framework import serializers
from .models import Lunch
from api_providers.models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'


class LunchSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(many=False, read_only=True)

    class Meta:
        model = Lunch
        fields = '__all__'

