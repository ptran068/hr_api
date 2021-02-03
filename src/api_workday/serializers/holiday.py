from rest_framework import serializers

from api_workday.models import Holiday


class HolidaysSerizlizer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = '__all__'
