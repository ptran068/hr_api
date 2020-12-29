from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_identity import UserIdentity
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.serializers.related_profile import UserIdentitySerializer
import factory


class UserIdentityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserIdentity

    identity_number = factory.Faker('random_int')
    issue_date = factory.Faker('date')
    issue_place = factory.Faker('name')
    place_of_birth = factory.Faker('name')


class UserIdentityTests(APITestCase):

    def setUp(self):
        self.UserIdentity = UserIdentityFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user_identity = UserIdentityFactory.create(user=self.user)
        self.valid_data = {
            "identity_number": "1231231231",
            "issue_date": "2020-01-01",
            "issue_place": "DN",
            "place_of_birth": "DN"
        }
        self.invalid_data = {
            "identity_number": "",
        }

    def test_user_get_identity(self):
        url = reverse('identity-detail', kwargs={'pk': self.user.id})
        user_identity = self.UserIdentity.objects.get(user=self.user)
        data = UserIdentitySerializer(user_identity).data
        response = self.client.get(url)
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_identity(self):
        temp_user = UserFactory.build()
        url = reverse('identity-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_identity(self):
        user_auth = authentication(self)
        self.client.credentials(HTTP_AUTHORIZATION=user_auth[0])
        temp_user = user_auth[1]
        url = reverse('identity-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_identity(self):
        temp_user = UserFactory.create()
        url = reverse('identity-add',  kwargs={'pk': temp_user.id})
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_identity(self):
        url = reverse('identity-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_invalid_identity(self):
        url = reverse('identity-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_delete_identity(self):
        url = reverse('identity-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_identity(self):
        url = reverse('identity-detail', kwargs={'pk': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
