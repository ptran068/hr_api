import factory
from faker import Factory

from .type_off import TypeOffFactory
from api_workday.models import RequestOff

faker = Factory.create()


class RequestOffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestOff

    reason = faker.word()
    type_off = factory.SubFactory(TypeOffFactory)
