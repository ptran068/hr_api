from rest_framework import serializers

from api_workday.models.date_off import DateOff
from api_workday.models.type_off import TypeOff
from api_workday.models.request_off import RequestOff


class TypeOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeOff
        fields = '__all__'


class RequestOffSerializer(serializers.ModelSerializer):
    type_off = TypeOffSerializer(read_only=True)

    class Meta:
        model = RequestOff
        fields = ['id', 'type_off', 'reason']


class DateOffForCalendarSerializer(serializers.ModelSerializer):
    request_off = RequestOffSerializer(read_only=True)

    class Meta:
        model = DateOff
        fields = ['id', 'request_off', 'date', 'type', 'lunch']
