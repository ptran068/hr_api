from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_banks import UserBanks, Banks
from api_user.tests.factories import UserFactory, authentication
from api_user.serializers.related_profile import UserBanksSerializer
import factory


class BanksFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Banks

    name = factory.Faker('name')


class UserBanksFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserBanks

    account_number = factory.Faker('random_int')
    branch = factory.Faker('address')


class UserBanksTests(APITestCase):

    def setUp(self):
        self.UserBanks = UserBanksFactory._meta.model
        self.Banks = BanksFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.bank = BanksFactory.create()
        self.user_bank = UserBanksFactory.create(user=self.user, bank=self.bank)
        self.valid_data = {
            "account_number": "123123123123",
            "bank": f"{self.bank.id}",
            "branch": "Da Nang"
        }
        self.invalid_data = {
            "account_number": "",  # not allow null
        }

    def test_user_get_bank(self):
        url = reverse('bank-detail', kwargs={'pk': self.user.id})
        user_bank = self.UserBanks.objects.get(user=self.user)
        data = UserBanksSerializer(user_bank).data
        response = self.client.get(url)
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_bank(self):
        temp_user = UserFactory.build()
        url = reverse('bank-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_bank(self):
        user_auth = authentication(self)
        self.client.credentials(HTTP_AUTHORIZATION=user_auth[0])
        temp_user = user_auth[1]
        url = reverse('bank-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_bank(self):
        temp_user = UserFactory.create()
        url = reverse('bank-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_bank(self):
        url = reverse('bank-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_invalid_bank(self):
        url = reverse('bank-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_delete_bank(self):
        url = reverse('bank-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_bank(self):
        url = reverse('bank-detail', kwargs={'pk': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
