from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from api_team.models.team import Team
from api_user.tests.factories import UserFactory, ProfileFactory, authentication
from api_user.constants.titles import Titles
import factory


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team


class TeamTests(APITestCase):

    def setUp(self):
        self.Team = Team._meta.model
        self.authentication = authentication(self, staff=True)
        self.user = self.authentication[1]
        self.pm = UserFactory.create()
        self.pm_profile = ProfileFactory(user=self.pm)
        self.member = UserFactory.create()
        self.memberProfile = ProfileFactory(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication[0])
        self.team = TeamFactory.create(team_name=factory.Faker('name'), team_email=factory.Faker('email'), team_leader=self.user)

    # Add PM: Admin
    # Add team members, leaders: Admin / PM

    def test_admin_add_pm(self):
        url = reverse('team-set-project-manager', kwargs={'pk': self.team.id})
        data = { 'email': f'{self.pm.email}' }
        response = self.client.put(url, data)
        team = self.Team.objects.get(pk=self.team.id)
        self.assertEqual(team.project_manager, self.pm)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_add_pm(self):
        url = reverse('team-set-project-manager', kwargs={'pk': self.team.id})
        nadmin_authentication = authentication(self, staff=False)
        self.client.credentials(HTTP_AUTHORIZATION=nadmin_authentication[0])
        data = { 'email': f'{self.pm.email}' }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_add_member(self):
        url = reverse('team-add-member', kwargs={'pk': self.team.id})
        data = { 'emails': f'{self.member.email}' }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pm_add_member(self):
        url = reverse('team-add-member', kwargs={'pk': self.team.id})
        pm_authentication = authentication(self, staff=False)
        self.client.credentials(HTTP_AUTHORIZATION=pm_authentication[0])
        pm_authentication[1].title = Titles.TITLES[2][0]
        pm_authentication[1].save()
        self.team.project_manager = pm_authentication[1]
        self.team.save()
        data = { 'emails': f'{self.member.email}' }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_and_pm_add_member(self):
        url = reverse('team-add-member', kwargs={'pk': self.team.id})
        temp_authentication = authentication(self, staff=False)
        self.client.credentials(HTTP_AUTHORIZATION=temp_authentication[0])
        data = { 'emails': f'{self.member.email}' }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

