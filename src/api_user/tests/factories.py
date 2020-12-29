from api_user.models import User, Profile
from rest_framework.test import APIClient
import factory
import json


title_list = ['Project manager', 'Developer']
name_list = ['do nguyen', 'phong tran', 'hien doan', 'dat nguyen', 'luan nguyen']
email_list = ['donguyen@gmail.com', 'phongtran@gmail.com', 'hiendoan@gmail.com', 'datnguyen@gmail.com', 'luannguyen@gmail.com']
birthday_list = ['1998-06-01', '1998-07-01', '1998-05-01', '1998-10-01', '1998-11-01']
gender = ['other', 'male', 'female']
joindate_list = ['2020-06-01', '2019-07-01', '2019-05-01', '2020-10-01', '2020-11-01']
team_list = ['team 1', 'team 2', 'team 3', 'team 4']
user_password = '123456'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'staff', 'title')

    email = factory.Faker('email')
    title = factory.Faker('name')
    password = factory.PostGenerationMethodCall('set_password', user_password)
    staff = False


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    name = factory.Faker('name')


def authentication(self, staff=False):
    user = UserFactory(staff=staff)
    url = '/api/v1/login/'
    profile = ProfileFactory(user=user, name='Test')
    payload = {
        'email': user.email,
        'password': user_password
    }
    res = self.client.post(url, data=payload)
    response_data = json.loads(res.content)
    token = response_data.get('token')
    return [token, user]
