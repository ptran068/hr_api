from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.models.user_family_members import UserFamilyMembers
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.serializers.related_profile import UserFamilyMembersSerializer
import factory


class UserFamilyMembersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserFamilyMembers

    name = factory.Faker('name')
    date_of_birth = factory.Faker('date')
    relationship = "CHILD"  # this is choices type so can not faker


class UserFamilyMembersTests(APITestCase):

    def setUp(self):
        self.UserFamilyMembers = UserFamilyMembersFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user_family = UserFamilyMembersFactory.create(user=self.user)
        self.valid_data = {
            "name": "abcxyz",
            "date_of_birth": "2020-01-01",
            "relationship": "CHILD",
        }
        self.invalid_data = {
            "name": ""
        }

    def test_user_get_family(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_invalid_family(self):
        temp_user = UserFactory.build()
        url = reverse('family-detail', kwargs={'pk': temp_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_family(self):
        url = reverse('family-add', kwargs={'pk': self.user.id})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_family(self):
        url = reverse('family-add', kwargs={'pk': self.user.id})
        response = self.client.post(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_family(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        self.valid_data['id'] = self.user_family.id
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_not_owner_family(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        self.valid_data['id'] = self.user_family.id
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_invalid_family(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_delete_family(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        data = {"id": f"{self.user_family.id}"}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_family_invalid(self):
        url = reverse('family-detail', kwargs={'pk': self.user.id})
        data = {"id": ""}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
