from .models import Provider
import factory
import json
from faker import Factory
faker = Factory.create()


class ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Provider
        django_get_or_create = ('name', 'link', 'description', 'phone', 'address')

    name = faker.name()
    link = faker.text(10)
    description = faker.text(10)
    phone = faker.text(10)
    address = faker.text(10)
