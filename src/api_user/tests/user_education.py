from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_education import UserEducation
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.serializers.related_profile import UserEducationSerializer
import factory


class UserEducationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserEducation

    school = factory.Faker('name')
    degree = factory.Faker('name')
    field_of_study = factory.Faker('name')
    graduated_year = factory.Faker('random_int')


class UserEducationTests(APITestCase):

    def setUp(self):
        self.UserEducation = UserEducationFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user_education = UserEducationFactory.create(user=self.user)
        self.valid_data = {
            "school": "bkdn",
            "degree": "master",
            "field_of_study": "it",
            "graduated_year": "2000",
        }
        self.invalid_data = {
            "school": ""
        }

    def test_user_get_education(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_education(self):
        temp_user = UserFactory.build()
        url = reverse('education-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_education(self):
        url = reverse('education-add', kwargs={'pk': self.user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_education(self):
        url = reverse('education-list')
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_education(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        self.valid_data['id'] = self.user_education.id
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_not_owner_education(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        self.valid_data['id'] = self.user_education.id
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_invalid_education(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_delete_education(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        data = {"education_id": f"{self.user_education.id}"}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_education_invalid(self):
        url = reverse('education-detail', kwargs={'pk': self.user.id})
        data = {"education_id": ""}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
