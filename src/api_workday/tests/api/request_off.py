import json
import random
import uuid

from django.urls import reverse
from faker import Factory
from rest_framework import status
from rest_framework.test import APITestCase

from api_workday.factories import TypeOffFactory
from api_workday.factories.company import CompanyFactory
from api_workday.factories.request_off import RequestOffFactory
from api_workday.models.request_off import RequestOff
from api_workday.utils.user_auth import authentication, UserFactory, ProfileFactory
from api_workday.serializers.request_off import RequestOffSerializer

faker = Factory.create()


class RequestOfTesting(APITestCase):
    def setUp(self):
        self.uuid_cus = uuid.uuid1(random.randint(0, 2 ** 48 - 1))
        self.admin = UserFactory()
        self.profile = ProfileFactory(user=self.admin)

        self.user1 = UserFactory()
        self.user1_profile = ProfileFactory.create(user=self.user1)

        self.user2 = UserFactory()
        self.user2_profile = ProfileFactory.create(user=self.user2, line_manager=self.user1_profile)
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user2))

        self.company = CompanyFactory()

        self.request_off = RequestOffFactory(profile=self.profile)
        self.lenRequestOff = RequestOff.objects.count()

        self.type_off = TypeOffFactory()

        self.valid_data = {
            "reason": 'Hello',
            "type_id": self.type_off.id,
            "date": [{"date": "2026-09-30", "type": "All day", "lunch": "False"},
                     {"date": "2025-09-30", "type": "Morning", "lunch": "True"}]
        }

        self.url_request = '/api/v1/workday/request/create'

    #GET
    def test_get_request_off(self):
        url = reverse('request-detail', args=[self.request_off.id])
        request_off = RequestOff.objects.get(pk=self.request_off.id)
        serializer = RequestOffSerializer(request_off)
        response = self.client.get(url)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('id'), serializer.data.get('id'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_off_with_out_credential(self):
        url = reverse('request-detail', args=[self.request_off.id])
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # CREATE
    def test_create_request_off_with_valid_input(self):
        response = self.client.post(self.url_request, data=self.valid_data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('reason'), self.valid_data.get('reason'))
        self.assertEqual(RequestOff.objects.count() - self.lenRequestOff, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_request_off_without_credential(self):
        url = reverse('create-request')
        self.client.credentials()
        response = self.client.post(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_request_off_with_invalid_input(self):
        url = reverse('create-request')
        data = {
            "reason": '',
            "date": [{"date": "2026-09-30", "type": "All day", "lunch": "False"},
                     {"date": "2025-09-30", "type": "Morning", "lunch": "True"}]
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #EDIT
    def test_edit_request_off_with_out_credential(self):
        url = reverse('request-detail', args=[self.request_off.id])
        self.client.credentials()
        response = self.client.put(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_request_off(self):
        url = reverse('request-detail', args=[self.request_off.id])
        request_off = RequestOff.objects.get(pk=self.request_off.id)
        serializer = RequestOffSerializer(request_off)
        response = self.client.put(url, data=self.valid_data)
        response_data = json.loads(response.content)
        self.assertNotEqual(response_data.get('reason'), serializer.data.get('reason'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_request_off_with_invalid_id(self):
        url = reverse('request-detail', args=[self.uuid_cus])
        response = self.client.put(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    #DELETE
    def test_delete_request_off_with_out_credential(self):
        url = reverse('request-detail', args=[self.request_off.id])
        self.client.credentials()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_request_off(self):
        url = reverse('request-detail', args=[self.request_off.id])
        response = self.client.delete(url)
        self.assertEqual(RequestOff.objects.count() - self.lenRequestOff, -1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_request_off_with_invalid_id(self):
        url = reverse('request-detail', args=[self.uuid_cus])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
