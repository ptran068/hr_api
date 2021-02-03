from rest_framework import serializers

from api_workday.models.type_off import TypeOff


class TypeOffSerizlizer(serializers.ModelSerializer):

    class Meta:
        model = TypeOff
        fields = '__all__'
