import factory
from faker import Factory
from .models import Lunch

faker = Factory.create()


class LunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lunch
        django_get_or_create = ('date', 'has_veggie')

    date = '2020-10-05'
    has_veggie = faker.boolean()

