import factory
from django.core.files.base import ContentFile
from faker import Factory

from .models import Company

faker = Factory.create()


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name', 'link', 'logo', 'address', 'descriptions')

    name = faker.word()
    link = faker.word()
    address = faker.word()
    descriptions = faker.text()
    logo = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data(
                {'width': 1024, 'height': 768}
            ), 'example.jpg'
        )
    )
