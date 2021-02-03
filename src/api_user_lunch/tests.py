
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api_lunch.factory import LunchFactory
from api_providers.factory import ProviderFactory
from .models import UserLunch
import random
import uuid
from utils.fake_auth import authentication, admin_authentication, UserFactory, ProfileFactory
from .factory import UserLunchFactory
from faker import Factory
import datetime
today = datetime.date.today()
faker = Factory.create()


class UserLunchTesting(APITestCase):
    def setUp(self):
        self.name = faker.name(),
        self.auth = authentication(self)
        self.auth_admin = admin_authentication(self)
        self.client.credentials(HTTP_AUTHORIZATION=self.auth[0])
        self.fake_uuid = uuid.uuid1(random.randint(0, 2 ** 48 - 1))
        self.fake_normal_user = UserFactory()
        self.fake_admin_user = UserFactory(admin=True, is_superuser=True, staff=True)
        self.fake_normal_profile = ProfileFactory(user=self.fake_normal_user, name=self.name)
        self.fake_admin_profile = ProfileFactory(user=self.fake_admin_user, name=self.name)
        self.fake_provider = ProviderFactory()
        self.fake_lunch = LunchFactory(provider=self.fake_provider)

        self.fake_user_lunch = UserLunchFactory(lunch=self.fake_lunch, profile_id=self.auth[1])
        self.fake_user_lunch_today = UserLunchFactory(lunch=self.fake_lunch, profile_id=self.auth[1], date=today)

    # CREATE
    def test_create_user_lunch_with_invalid_lunch_id(self):
        url = reverse('create-user-lunch')
        data = {
            'date': faker.date(),
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch': self.fake_uuid,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_create_user_lunch_with_at_weekend(self):
        url = reverse('create-user-lunch')
        data = {
            'date': '2020-10-11',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['error_msg'], 'Cant set lunch at weekend')

    def test_create_user_lunch_with_at_existed_date(self):
        url = reverse('create-user-lunch')
        data = {
            'date': '2030-10-10',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['error_msg'], 'user_lunch have been created with date 2030-10-10')

    def test_create_user_lunch_with_date_smaller_than_today(self):
        url = reverse('create-user-lunch')
        data = {
            'date': '2020-09-10',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['error_msg'], 'Create Error')

    def test_create_user_lunch_with_invalid_date(self):
        url = reverse('create-user-lunch')
        data = {
            'date': '2020-10-',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['date'][0], 'Date has wrong format. Use one of these formats '
                                                             'instead: YYYY-MM-DD.')

    def test_create_user_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('create-user-lunch')
        data = {
            'date': '2020-10-15',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_create_user_lunch(self):
        url = reverse('create-user-lunch')
        data = {
            'date': '2024-10-09',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserLunch.objects.count(), 3)
        self.assertEqual(json.loads(res.content)['date'], '2024-10-09')

    def test_create_user_lunch_with_admin_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('create-user-lunch')
        data = {
            'date': '2024-10-09',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserLunch.objects.count(), 3)
        self.assertEqual(json.loads(res.content)['date'], '2024-10-09')

    # CREATE MANY

    def test_create_many_user_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('create-many-user-lunch')
        data = {
            'date': '2020-10-15',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_create_many_user_lunch_without_list_dates(self):
        url = reverse('create-many-user-lunch')
        data = {
            'date': '2020-10-15',
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }

        res = self.client.post(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['error_msg'], 'list_dates are empty')

    def test_create_many_user_lunch_with_list_dates_contain_weekend_dates(self):
        url = reverse('create-many-user-lunch')
        data = {
            'list_dates': ['2022-10-13', '2023-10-12', '2020-10-11', '2020-10-10'],
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 4)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 2 days')

    def test_create_many_user_lunch_with_valid_input(self):
        url = reverse('create-many-user-lunch')
        data = {
            'list_dates': ['2022-10-13', '2023-10-12', '2024-10-09'],
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 5)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 3 days')

    def test_create_many_user_lunch_with_admin_rule(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('create-many-user-lunch')
        data = {
            'list_dates': ['2022-10-13', '2023-10-12', '2024-10-09'],
            'has_veggie': faker.boolean(),
            'profile_id': self.auth[1],
            'lunch_id': self.fake_lunch.id,
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 5)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 3 days')

    # Admin create
    def test_admin_create_many_user_lunch_with_valid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('admin-create-user-lunch')
        data = {
            'list_data': [
                {
                    'date': '2020-10-15',
                    'has_veggie': faker.boolean()
                },
                {
                    'date': '2020-10-15',
                    'has_veggie': faker.boolean()
                }
            ]
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 4)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 2 days')

    def test_admin_create_many_user_lunch_with_normal_user(self):
        url = reverse('admin-create-user-lunch')
        data = {
            'list_data': [
                {
                    'date': '2020-10-15',
                    'has_veggie': faker.boolean()
                },
                {
                    'date': '2020-10-15',
                    'has_veggie': faker.boolean()
                }
            ]
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    def test_admin_create_many_user_lunch_with_invalid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('admin-create-user-lunch')
        data = {
            'list_data': []
        }
        res = self.client.post(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['error_msg'], 'list_data is empty')

    # Update
    def test_update_user_lunch_with_invalid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-user-lunch', args=[self.fake_user_lunch.id])
        data = {
            'has_veggie': faker.boolean(),
            'lunch': faker.date()
        }
        res = self.client.put(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_update_user_lunch_with_valid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-user-lunch', args=[self.fake_user_lunch.id])
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.put(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['has_veggie'], True)

    def test_update_user_lunch_without_authentication(self):
        self.client.credentials()
        url = reverse('modify-user-lunch', args=[self.fake_user_lunch.id])
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.put(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_delete_user_lunch_without_authentication(self):
        self.client.credentials()
        url = reverse('modify-user-lunch', args=[self.fake_user_lunch.id])
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.delete(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_delete_user_lunch_with_today_greater_than_lunch_date(self):
        url = reverse('modify-user-lunch', args=[self.fake_uuid])
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.delete(url, data=data)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['msg'], 'Cant delete lunch with date lunch little than now')

    def test_delete_user_lunch(self):
        url = reverse('modify-user-lunch', args=[self.fake_user_lunch_today.id])
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.delete(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 1)

    def test_get_user_lunches(self):
        url = reverse('get-user-lunches')
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.get(url, data=data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(len(json.loads(res.content)), 2)

    def test_get_user_lunches_without_credential(self):
        self.client.credentials()
        url = reverse('get-user-lunches')
        data = {
            'has_veggie': True,
            'lunch_id': self.fake_lunch.id
        }
        res = self.client.get(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(len(json.loads(res.content)), 1)

    # Set Veggie

    def test_set_veggie_user_lunches_without_credential(self):
        self.client.credentials()
        url = reverse('set-veggie-lunch')
        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_set_veggie_user_lunches_with_not_found_lunar_day(self):
        url = reverse('set-veggie-lunch')
        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['msg'], 'Not found lunar day')

    def test_set_veggie_user_lunches(self):
        url = reverse('set-veggie-lunch')
        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 2)

    # Cancel Veggie

    def test_cancel_veggie_user_lunches_without_credential(self):
        self.client.credentials()
        url = reverse('cancel-veggie-lunch')
        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_cancel_veggie_user_lunches(self):
        url = reverse('cancel-veggie-lunch')
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just cancel setting veggie lunch for this month')

    # statistic
    def test_statistic_user_lunches_without_credential(self):
        self.client.credentials()
        url = reverse('statistic-user-lunch')
        data = {
            'is_month': True,
            'date': '2020-10-10'
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_delete_many_user_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('delete-many-user-lunch')
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserLunch.objects.count(), 2)

    def test_delete_many_user_lunch(self):
        url = reverse('delete-many-user-lunch')
        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['msg'], 'Deleted successfully from today to the end up month')


