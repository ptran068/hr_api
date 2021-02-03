import io
import json

from PIL import Image
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api_company.factories import CompanyFactory
from api_company.models import Company
from api_company.utils.user_auth import UserFactory, ProfileFactory, authentication


class CompanyTesting(APITestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.lenCompany = 0
        self.admin = UserFactory()
        self.profile = ProfileFactory(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.input_data = {
            "link": "http://paradox.ai",
            "name": "Paradox",
            "descriptions": "No have",
            "logo": self.generate_photo_file()
        }

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    # GET
    def test_get_company(self):
        url = reverse('company')
        response = self.client.get(url)
        self.assertEqual(json.loads(response.content)['id'], str(self.company.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # CREATE
    def test_create_company_with_valid_input(self):
        self.company.delete()
        url = reverse('create-company')
        input_data = {
            "link": "http://paradox.ai",
            "name": "Paradox",
            "descriptions": "No have",
        }
        response = self.client.post(url, data=self.input_data, format='multipart')
        response_data = json.loads(response.content)
        create_data = {
            "link": response_data["link"],
            "name": response_data["name"],
            "descriptions": response_data["descriptions"]
        }
        self.assertEqual(create_data, input_data)
        self.assertEqual(Company.objects.count() - self.lenCompany, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_company_when_have_one_objects_in_db(self):
        url = reverse('create-company')
        response = self.client.post(url, data=self.input_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_company_without_credential(self):
        url = reverse('create-company')
        self.client.credentials()
        response = self.client.post(url, data=self.input_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # EDIT
    def test_edit_company_without_credential(self):
        url = reverse('modify-company')
        self.client.credentials()
        response = self.client.patch(url, data=self.input_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #
    def test_edit_company_with_valid_input(self):
        url = reverse('modify-company')
        modify_data = {
            "link": "http://paradox.ai",
            "name": "Paradox",
            "descriptions": "No have",
        }
        response = self.client.patch(url, data=self.input_data, format='multipart')
        response_data = json.loads(response.content)
        create_data = {
            "link": response_data["link"],
            "name": response_data["name"],
            "descriptions": response_data["descriptions"]
        }
        self.assertEqual(create_data, modify_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
