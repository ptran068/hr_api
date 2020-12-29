from api_user.models import User, Profile
import factory
import json
from faker import Factory
faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'staff')

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'default_password')
    staff = False


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile


def authentication(self):
    user = UserFactory()
    profile = ProfileFactory(user=user, name='admin')
    url = '/api/v1/login/'
    payload = {
        'email': user.email,
        'password': 'default_password'
    }
    res = self.client.post(url, data=payload)
    response_data = json.loads(res.content)
    token = response_data.get('token')
    profile_id = response_data.get('profile_id')

    return [token, profile_id]


def admin_authentication(self):
    user = UserFactory(
        admin=True,
        is_superuser=True,
        staff=True,
    )
    profile = ProfileFactory(user=user, name='admin')

    url = '/api/v1/login/'
    payload = {
        'email': user.email,
        'password': 'default_password'
    }
    res = self.client.post(url, data=payload)
    response_data = json.loads(res.content)
    token = response_data.get('token')
    profile_id = response_data.get('profile_id')

    return [token, profile_id]
