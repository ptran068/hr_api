import json

import factory
from faker import Factory
from rest_framework.test import APIClient

from api_user.models import User, Profile

faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'staff')

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    staff = True


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile


def authentication(user):
    client = APIClient()
    url = '/api/v1/login/'
    payload = {
        'email': user.email,
        'password': 'defaultpassword'
    }
    res = client.post(url, data=payload)
    response_data = json.loads(res.content)
    token = response_data.get('token')
    return token
