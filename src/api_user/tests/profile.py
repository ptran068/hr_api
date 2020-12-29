from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
import uuid


class ProfileTests(APITestCase):
    
    def setUp(self):
        self.User = UserFactory._meta.model
        self.Profile = ProfileFactory._meta.model
        self.authentication = authentication(self, staff=True)
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.user = self.authentication[1]
        self.user_profile = self.Profile.objects.get(user=self.user)
        self.manager = UserFactory.create()
        self.manager_profile = ProfileFactory.create(user=self.manager)


    def test_admin_set_line_manager(self):
        url = reverse('profile-set-line-manager', kwargs={ 'pk': self.user_profile.id })
        data = { 'name': f'{self.manager_profile.name}' }
        response = self.client.post(url, data)
        user_profile = self.Profile.objects.get(pk=self.user_profile.id)
        self.assertEqual(user_profile.line_manager.id, self.manager_profile.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_set_line_manager_not_exist(self):
        url = reverse('profile-set-line-manager', kwargs={ 'pk': self.user_profile.id })
        temp_user = UserFactory.build() # this have not saved to test database yet
        temp_user_profile = ProfileFactory.build(user=temp_user)
        data = { 'name': f'{temp_user_profile.name}' }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_set_line_manager_by_itself(self):
        url = reverse('profile-set-line-manager', kwargs={ 'pk': self.user_profile.id })
        data = { 'name': f'{self.user_profile.name}' }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_set_line_manager(self):
        url = reverse('profile-set-line-manager', kwargs={ 'pk': self.user_profile.id })
        data = { 'name': f'{self.manager_profile.name}' }
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_remove_line_manager(self):
        url = reverse('profile-remove-line-manager', kwargs={ 'pk': self.user_profile.id })
        response = self.client.delete(url)
        user_profile = self.Profile.objects.get(pk=self.user_profile.id)
        self.assertEqual(user_profile.line_manager, None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_remove_line_manager(self):
        url = reverse('profile-remove-line-manager', kwargs={ 'pk': self.user_profile.id })
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self)[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

