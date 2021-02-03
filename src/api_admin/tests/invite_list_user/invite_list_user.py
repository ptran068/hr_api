import json
import random
import uuid

from faker import Factory
from rest_framework import status
from rest_framework.test import APITestCase

from api_admin.utils.user_auth import authentication, UserFactory, ProfileFactory

faker = Factory.create()


class InviteListUserTesting(APITestCase):

    def setUp(self):
        self.uuid_cus = uuid.uuid1(random.randint(0, 2 ** 48 - 1))
        self.admin = UserFactory()
        self.profile = ProfileFactory(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.url = '/api/v1/admin/invite_list_user/'

    def test_invite_list_user_with_all_email_valid(self):
        data = [{'email': 'luan@paradox.ai', 'name': 'Luan'},
                {'email': 'nqluan@paradox.ai', 'name': 'Quang Luan'}]
        response = self.client.post(self.url, data)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['valid_user']), 2)
        self.assertEqual(len(response_data['invalid_user']), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invite_list_user_with_all_email_invalide(self):
        user = UserFactory(email='luan@paradox.ai', staff=False)
        profile = ProfileFactory(user=user)
        data = [{'email': 'luan@paradox.ai', 'name': 'Luan'},
                {'email': 'nqluan', 'name': 'Quang Luan'}]
        response = self.client.post(self.url, data)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['valid_user']), 0)
        self.assertEqual(len(response_data['invalid_user']), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_with_one_email_valid_one_email_invalid(self):
        data = [{'email': 'luan@paradox.ai', 'name': 'Luan'},
                {'email': 'nqluan', 'name': 'Quang Luan'}]
        response = self.client.post(self.url, data)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['valid_user']), 1)
        self.assertEqual(response_data['valid_user'][0].get('email'), data[0].get('email'))
        self.assertEqual(len(response_data['invalid_user']), 1)
        self.assertEqual(response_data['invalid_user'][0].get('email'), data[1].get('email'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_with_email_duplicate(self):
        data = [{'email': 'luan@paradox.ai', 'name': 'Luan'},
                {'email': 'luan@paradox.ai', 'name': 'Luan'},
                {'email': 'nqluan', 'name': 'Quang Luan'}]
        response = self.client.post(self.url, data)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['valid_user']), 1)
        self.assertEqual(len(response_data['invalid_user']), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)