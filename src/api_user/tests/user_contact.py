from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_contact import UserContact
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.serializers.related_profile import UserContactSerializer
import factory


class UserContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserContact

    permanent_address = factory.Faker('name')
    temporary_address = factory.Faker('name')
    household_registration_number = factory.Faker('random_int')
    contact_emergency = factory.Faker('random_int')


class UserContactTests(APITestCase):

    def setUp(self):
        self.UserContact = UserContactFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user_contact = UserContactFactory.create(user=self.authentication[1])
        self.valid_data = {
            "permanent_address": "1 abc",
            "temporary_address": "2 def",
            "household_registration_number": "123456",
            "contact_emergency": "1234567890",
        }
        self.invalid_data = {
            "permanent_address": "",  # not allow null
            "temporary_address": "",
            "household_registration_number": "",
            "contact_emergency": "",
        }

    def test_user_get_contact(self):
        url = reverse('contact-detail', kwargs={'pk': self.user.id})
        user_contact = self.UserContact.objects.get(user=self.user)
        data = UserContactSerializer(user_contact).data
        response = self.client.get(url)
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_contact(self):
        temp_user = UserFactory.build()
        url = reverse('contact-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_contact(self):
        user_auth = authentication(self)
        self.client.credentials(HTTP_AUTHORIZATION=user_auth[0])
        temp_user = user_auth[1]
        url = reverse('contact-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_contact(self):
        temp_user = UserFactory.create()
        url = reverse('contact-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_contact(self):
        url = reverse('contact-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_invalid_contact(self):
        url = reverse('contact-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_delete_contact(self):
        url = reverse('contact-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_contact(self):
        url = reverse('contact-detail', kwargs={'pk': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
