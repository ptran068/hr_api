from django.db import models
from rest_framework import serializers


class CompanyManager(models.Manager):
    def get_company(self):
        company = self.all().first()
        if company is None:
            raise serializers.ValidationError({'status': 'Data not found'})
        return company
