from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_insurance import UserInsurance
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.serializers.related_profile import UserInsuranceSerializer
import factory


class UserInsuranceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserInsurance

    social_insurance_code = factory.Faker('random_int')
    start_date = factory.Faker('date')


class UserInsuranceTests(APITestCase):

    def setUp(self):
        self.UserInsurance = UserInsuranceFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user_insurance = UserInsuranceFactory.create(user=self.user)
        self.valid_data = {
            "social_insurance_code": "abcxyz123",
            "start_date": "2020-01-01"
        }
        self.invalid_data = {
            "social_insurance_code": "",
        }

    def test_user_get_insurance(self):
        url = reverse('insurance-detail', kwargs={'pk': self.user.id})
        user_insurance = self.UserInsurance.objects.get(user=self.user)
        data = UserInsuranceSerializer(user_insurance).data
        response = self.client.get(url)
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_insurance(self):
        temp_user = UserFactory.build()
        url = reverse('insurance-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_insurance(self):
        user_auth = authentication(self)
        self.client.credentials(HTTP_AUTHORIZATION=user_auth[0])
        temp_user = user_auth[1]
        url = reverse('insurance-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_insurance(self):
        temp_user = UserFactory.create()
        url = reverse('insurance-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_insurance(self):
        url = reverse('insurance-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_invalid_insurance(self):
        url = reverse('insurance-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_delete_insurance(self):
        url = reverse('insurance-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_insurance(self):
        url = reverse('insurance-detail', kwargs={'pk': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
