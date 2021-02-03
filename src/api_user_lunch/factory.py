import factory
from faker import Factory
from .models import UserLunch
faker = Factory.create()


class UserLunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserLunch
        django_get_or_create = ('date', 'has_veggie')

    date = '2030-10-10'
    has_veggie = faker.boolean()

