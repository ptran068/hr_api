from rest_framework import serializers
from api_workday.models.request_detail import RequestDetail
from .request_off import RequestOffSerializer


class RequestDetailSerializer(serializers.ModelSerializer):
    request_off = RequestOffSerializer(many=False, read_only=True)

    class Meta:
        model = RequestDetail
        fields = '__all__'
