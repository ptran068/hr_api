import uuid

from django.db import models

from api_base.models import TimeStampedModel
from .managers import CompanyManager


def name_file(instance, filename):
    return '/'.join(['images', str(instance.id), filename])


class Company(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to=name_file, height_field=None, width_field=None, max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    descriptions = models.TextField(null=True, blank=True)
    maximum_level_approved = models.IntegerField(default=2, blank=True)
    expired_annual_leave_last_year = models.IntegerField(default=7, blank=True)

    objects = CompanyManager()

    class Meta:
        db_table = 'hr_company'
