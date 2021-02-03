from django.urls import reverse
from rest_framework import status
from faker import Factory
from rest_framework.test import APITestCase
from api_workday.utils.user_auth import UserFactory, ProfileFactory, authentication
from api_user.models import Profile
# from api_workday.services import RemainLeaveService
from api_workday.models import RemainLeave
import json

faker = Factory.create()
import datetime


class RemainTesting(APITestCase):

    def setUp(self):
        self.admin = UserFactory()
        self.admin_profile = ProfileFactory.create(user=self.admin, join_date="2017-06-20")

        self.user = UserFactory(staff=False)
        self.user_profile = ProfileFactory.create(user=self.user, join_date="2015-02-15")

        self.user2 = UserFactory(staff=False)
        self.user_profile2 = ProfileFactory.create(user=self.user2, join_date="2020-05-10")

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.bonus = 1.0
        self.year = '2020'
        self.annual_leave_user1 = 17
        self.annual_leave_user2 = 8

    def test_create_remain_leave(self):
        response = self.client.post(reverse('create_remain_leave'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Profile.objects.all()), len(response.data))
        for remain in response.data:
            if remain['profile']['id'] == str(self.user_profile.id):
                self.assertEqual(remain['annual_leave'], self.annual_leave_user1)
            if remain['profile']['id'] == str(self.user_profile2.id):
                self.assertEqual(remain['annual_leave'], self.annual_leave_user2)

    def test_non_admin_create_remain_leave(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user))
        response = self.client.post(reverse('create_remain_leave'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(RemainLeave.objects.filter(year=self.year)), 0)

    def test_non_auth_create_remain_leave(self):
        self.client.credentials()
        response = self.client.post(reverse('create_remain_leave'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(RemainLeave.objects.filter(year=self.year)), 0)

    def test_get_retrieve_date_statistic(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user))
        response = self.client.get(reverse('retrieve_date_statistic'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)['profile']['id'], str(self.user_profile.id))

    def test_non_auth_get_retrieve_date_statistic(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})
        self.client.credentials()
        response = self.client.get(reverse('retrieve_date_statistic'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_bonus(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})


        present_bonus = RemainLeave.objects.get(year=self.year, profile_id=self.user_profile.id).bonus
        response = self.client.post(reverse('add_bonus'),
                                    data={"user_id": self.user.id, "bonus": self.bonus})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)['profile']['id'], str(self.user_profile.id))
        self.assertEqual(json.loads(response.content)["bonus"], float(present_bonus) + self.bonus)

    def test_add_bonus_with_invalid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})
        response = self.client.post(reverse('add_bonus'),
                                    data={"profile_id": "profile_id", "bonus": "bonus"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_admin_add_bonus(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user))
        response = self.client.post(reverse('add_bonus'),
                                    data={"profile_id": self.user_profile.id, "bonus": self.bonus})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_auth_add_bonus(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.admin))
        self.client.post(reverse('create_remain_leave'), data={"year": self.year})
        self.client.credentials()
        response = self.client.post(reverse('add_bonus'),
                                    data={"profile_id": self.user_profile.id, "bonus": self.bonus})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
