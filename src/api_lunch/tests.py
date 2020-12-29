import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api_lunch.factory import LunchFactory
from api_providers.models import Provider
import random
from .models import Lunch
import uuid
from utils.fake_auth import authentication, admin_authentication, UserFactory, ProfileFactory
from faker import Factory

faker = Factory.create()


class LunchTesting(APITestCase):
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
        self.fake_provider = Provider.objects.create(
            name=self.name,
            phone='122222',
            budget='10000',
            address=faker.text(5),
            link=faker.text(5)
        )
        self.fake_lunch = LunchFactory(provider=self.fake_provider)
        self.validData = {
            'has_veggie': True,
            'note': 'note',
            'provider': self.fake_provider.id,
            'date': '2020-11-11',
        }
        self.list_valid_input = {
            "list_lunches": [
                {
                    "list_dates": ["2020-10-09", "2020-10-11", "2020-10-13", "2020-10-15"],
                    "provider": self.fake_provider.id
                },
                {
                    "list_dates": ["2020-10-06", "2020-10-17", "2020-10-18"],
                    "provider": self.fake_provider.id
                }
            ]
        }

    # CREATE
    def test_create_lunch_with_valid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('create-lunch')
        res = self.client.post(url, data=self.validData)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lunch.objects.count(), 2)
        self.assertEqual(json.loads(res.content)['date'], '2020-11-11')

    def test_create_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('create-lunch')
        res = self.client.post(url, data=self.validData)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'Authentication credentials were not provided.')


    def test_create_lunch_with_existed_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('create-lunch')
        data = {
            'has_veggie': faker.boolean(),
            'provider': self.fake_provider.id,
            'date': '2020-10-05',
        }
        res = self.client.post(url, data=data)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['error_msg'], 'Lunch have been created with date 2020-10-05')

    def test_create_lunch_with_no_permission(self):
        url = reverse('create-lunch')
        data = {
            'has_veggie': faker.boolean(),
            'provider': self.fake_provider.id,
            'date': '2020-10-05',
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    def test_create_lunch_with_invalid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])

        url = reverse('create-lunch')
        data = {
            'has_veggie': faker.boolean(),
            'provider': self.fake_provider.id,
            'date': '2020-10-',
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['date'][0], 'Date has wrong format. Use one of these formats '
                                                             'instead: YYYY-MM-DD.')

    # CREATE Many
    def test_create_many_lunch_with_valid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('lunches')
        res = self.client.post(url, data=self.list_valid_input)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Lunch.objects.count(), 8)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 7 days')

    def test_create_many_lunch_with_duplicated_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('lunches')
        data = {
            "list_lunches": [
                {
                    "list_dates": ["2020-10-09", "2020-10-11", "2020-10-13", "2020-10-15"],
                    "provider": self.fake_provider.id
                },
                {
                    "list_dates": ["2020-10-09", "2020-10-13", "2020-10-16"],
                    "provider": self.fake_provider.id
                }
            ]
        }
        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Lunch.objects.count(), 6)
        self.assertEqual(json.loads(res.content)['msg'], 'You have just created lunch for 5 days')

    def test_create_many_lunch_without_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('lunches')
        data = {
            "list_lunches": []
        }
        res = self.client.post(url, data=data)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['error_msg'], 'list_lunches are empty')

    def test_create_many_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('lunches')
        res = self.client.post(url, data=self.list_valid_input)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'Authentication credentials were not provided.')

    def test_create_many_lunch_with_no_permission(self):
        url = reverse('lunches')
        res = self.client.post(url, data=self.list_valid_input)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    def test_create_many_lunch_with_invalid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('lunches')
        data = {
            "list_lunches": [
                {
                    "list_dates": ["2020-10-"],
                    "provider": self.fake_provider.id
                }
            ]
        }
        res = self.client.post(url, data=data)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['error_msg'], "time data '2020-10-' does not match format '%Y-%m-%d'")

    # UPDATE
    def test_update_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        res = self.client.put(url, data=self.validData)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)

    def test_update_lunch_with_valid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        data = {
            'date': '2020-10-10',
            'note': 'note'
        }
        res = self.client.put(url, data=data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['date'], '2020-10-10')

    def test_update_lunch_with_invalid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        data = {
            'has_veggie': self.name,
            'note': faker.text(5),
        }
        res = self.client.put(url, data=data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['has_veggie'][0], 'Must be a valid boolean.')

    def test_update_lunch_with_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-lunch', args=[self.fake_uuid])
        res = self.client.put(url, data=self.validData)
        self.assertEqual(json.loads(res.content)['error_msg'], 'lunch is empty')
        self.assertEqual(Lunch.objects.count(), 1)

    def test_update_lunch_with_no_permission(self):
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        data = {
            'date': '2020-10-10',
            'note': 'note'
        }
        res = self.client.put(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    # DELETE
    def test_delete_lunch_without_credential(self):
        self.client.credentials()
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'Authentication credentials were not provided.')

    def test_delete_lunch_with_no_permission(self):
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    def test_delete_lunch(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('modify-lunch', args=[self.fake_lunch.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lunch.objects.count(), 0)

    #  GET
    def test_get_lunches_without_credential(self):
        self.client.credentials()
        url = reverse('lunches')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'Authentication credentials were not provided.')

    def test_get_lunches_with_no_permission(self):
        url = reverse('lunches')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(json.loads(res.content)['detail'], 'You do not have permission to perform this action.')

    def test_get_lunches(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin[0])
        url = reverse('lunches')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Lunch.objects.count(), 1)
        self.assertEqual(len(json.loads(res.content)), 1)

