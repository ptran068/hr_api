import factory
from faker import Factory

from api_workday.models import TypeOff

faker = Factory.create()
class TypeOffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TypeOff
        django_get_or_create = ('title', 'type', 'descriptions', 'add_sub_day_off')

    title = 'Test'
    type = 0
    add_sub_day_off = 0
    descriptions = faker.text()
