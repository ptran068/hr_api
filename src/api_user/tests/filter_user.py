from random import randint
from rest_framework.test import APITestCase

from rest_framework import status
from api_user.tests.factories import UserFactory, ProfileFactory, authentication

import json, datetime


title_list = ['Project manager', 'Developer']
name_list = ['do nguyen', 'phong tran', 'hien doan', 'dat nguyen', 'luan nguyen']
birthday_list = ['1998-06-01', '1998-07-01', '1998-05-01', '1998-10-01', '1998-11-01']
gender_list = ['other', 'male', 'female']
joindate_list = ['2020-06-01', '2019-07-01', '2019-05-01', '2020-10-01', '2020-11-01']

NUMBER_OF_SAMPLE = 20

class TestFilterUser(APITestCase):

    def setUp(self):
        self.User = UserFactory._meta.model
        self.Profile = ProfileFactory._meta.model
        self.list_user = []
        for i in range(NUMBER_OF_SAMPLE):
            temp_user = UserFactory(title=title_list[randint(0, len(title_list) - 1)])
            _ = ProfileFactory(user=temp_user,
                               name=name_list[randint(0, len(name_list) - 1)],
                               birth_day=birthday_list[randint(0, len(birthday_list) - 1)],
                               gender=gender_list[randint(0, len(gender_list) - 1)],
                               join_date=joindate_list[randint(0, len(joindate_list) - 1)],)
            self.list_user.append(temp_user)
        self.authentication = authentication(self, staff=True)
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])

    def test_search_by_name(self):
        search_name = "dat"
        url = f'/api/v1/user/search?name={search_name}&page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        result_data = json.loads(response.content).get('results')
        random_result_data_name = result_data[randint(0, len(result_data) - 1)].get('profile').get('name')
        expected_result_length = self.Profile.objects.filter(name__icontains=search_name).count()
        self.assertIn(search_name, random_result_data_name)
        self.assertEqual(len(result_data), expected_result_length)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_title(self):
        search_title = title_list[randint(0, len(title_list) - 1)]
        url = f'/api/v1/user/search?title={search_title}&page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        result_data = json.loads(response.content).get('results')
        random_result_data_title = result_data[randint(0, len(result_data) - 1)].get('title')
        expected_result_length = self.User.objects.filter(title__istartswith=search_title).count()
        self.assertIn(search_title, random_result_data_title)
        self.assertEqual(len(result_data), expected_result_length)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_birthday(self):
        search_birthday = randint(1, 12)
        url = f'/api/v1/user/search?birthday={str(search_birthday)}&page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        result_data = json.loads(response.content).get('results')
        if len(result_data) > 0:
            random_result_data_birthday = result_data[randint(0, len(result_data) - 1)].get('profile').get('birth_day')
            self.assertIn(str(search_birthday), random_result_data_birthday)
        expected_result_length = self.Profile.objects.filter(birth_day__month=search_birthday).count()
        self.assertEqual(len(result_data), expected_result_length)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_joindate(self):
        search_joindate = '2020-06'
        url = f'/api/v1/user/search?joindate={search_joindate}&page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        result_data = json.loads(response.content).get('results')
        if len(result_data) > 0:
            random_result_data_joindate = result_data[randint(0, len(result_data) - 1)].get('profile').get('join_date')
            self.assertIn(search_joindate, random_result_data_joindate)
        search_joindate = datetime.datetime.strptime(search_joindate, '%Y-%m')
        expected_result_length = self.Profile.objects.filter(join_date__month=search_joindate.month, join_date__year=search_joindate.year).count()
        self.assertEqual(len(result_data), expected_result_length)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_gender(self):
        search_gender = gender_list[randint(0, len(gender_list) - 1)]
        url = f'/api/v1/user/search?gender={search_gender}&page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        result_data = json.loads(response.content).get('results')
        random_result_data_gender= result_data[randint(0, len(result_data) - 1)].get('profile').get('gender')
        expected_result_length = self.Profile.objects.filter(gender=search_gender).count()
        self.assertIn(search_gender, random_result_data_gender)
        self.assertEqual(len(result_data), expected_result_length)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_without_credential(self):
        self.client.credentials()
        url = f'/api/v1/user/search?page=1&page_size={NUMBER_OF_SAMPLE}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content)['detail'], 'Authentication credentials were not provided.')



