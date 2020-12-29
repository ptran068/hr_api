import factory
from faker import Factory

from api_workday.models import RequestDetail

faker = Factory.create()


class RequestDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestDetail
