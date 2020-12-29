from rest_framework import serializers

from api_company.models import Company


class CompanySerizlizer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
