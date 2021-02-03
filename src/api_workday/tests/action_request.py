import json
from django.urls import reverse
from rest_framework import status
from faker import Factory
from rest_framework.test import APITestCase
from api_workday.factories import TypeOffFactory
from api_workday.utils.user_auth import UserFactory, ProfileFactory, authentication
from api_workday.factories.company import CompanyFactory
from api_workday.constants import Workday
from api_workday.tests.validate_data.request_off import Request
from api_workday.tests.validate_data.action_request import ActionRequest
from api_workday.services.action_request import ActionRequestService
from uuid import UUID
from api_workday.factories.request_off import RequestOffFactory
from api_workday.factories.request_detail import RequestDetailFactory

faker = Factory.create()


class ActionRequestTesting(APITestCase):

    def setUp(self):
        self.user1 = UserFactory()
        self.user1_profile = ProfileFactory.create(user=self.user1)

        self.user2 = UserFactory(staff=False)
        self.user2_profile = ProfileFactory.create(user=self.user2, line_manager=self.user1_profile)

        self.user3 = UserFactory(staff=False)
        self.user3_profile = ProfileFactory.create(user=self.user3, line_manager=self.user2_profile)

        self.user4 = UserFactory(staff=False)
        self.user4_profile = ProfileFactory.create(user=self.user4, line_manager=self.user1_profile)

        self.company = CompanyFactory()

        self.type_off = TypeOffFactory()
        self.type_off_insurance = TypeOffFactory(type=1)
        self.request = Request.data(self.type_off.id)
        self.request_too_time = Request.data_too_time(self.type_off.id)
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user3))

        self.url_request = '/api/v1/workday/request/create'
        self.url_action = '/api/v1/workday/action'
        self.url_get_request = '/api/v1/workday/request/management'

        response_request = self.client.post(self.url_request, data=self.request)
        self.response_request_data = json.loads(response_request.content)

        response_request_too_time = self.client.post(self.url_request, self.request_too_time)
        self.data_request_too_time = json.loads(response_request_too_time.content)

        self.request_of_user_4 = RequestOffFactory(profile=self.user4_profile)
        self.request_detail = RequestDetailFactory(request_off=self.request_of_user_4, approve=self.user1_profile)

    def test_action_approved_request_with_two_line_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user2))

        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)

        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_FORWARDED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user1))
        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)
        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

    def test_action_approved_request_with_one_line_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user4))

        data_request = {
            "reason": faker.word(),
            "type_id": self.type_off.id,
            "date": [{"date": "2026-08-30", "type": "All day", "lunch": "False"}]
        }

        response = self.client.post(self.url_request, data=data_request)
        response_data = json.loads(response.content)

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user1))

        data = {
            'request_off_id': response_data['id'],
            'action': Workday.STATUS_APPROVED
        }

        response_action = self.client.post(self.url_action, data=data)
        response_action_data = json.loads(response_action.content)

        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

    def test_first_user_action_rejected_request_with_two_line_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user2))
        response_action = self.client.post(self.url_action, data=ActionRequest.reject(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)
        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_REJECTED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_REJECTED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user1))

        response_action = self.client.post(self.url_action, data=ActionRequest.reject(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_second_user_action_rejected_request_with_two_line_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user2))

        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)

        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_FORWARDED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_APPROVED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user1))

        response_action = self.client.post(self.url_action, data=ActionRequest.reject(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)

        self.assertEqual(response_action_data['request_off']['status'], Workday.STATUS_REJECTED)
        self.assertEqual(response_action_data['status'], Workday.STATUS_REJECTED)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

    def test_action_cancel_request_with_request_of_user(self):
        response_action = self.client.post(self.url_action, ActionRequest.cancel(self.response_request_data['id']))
        response_action_data = json.loads(response_action.content)
        self.assertEqual(response_action_data['status'], Workday.STATUS_CANCEL)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

    def test_actions_cancel_request_too_time_with_user(self):
        response_action = self.client.post(self.url_action, ActionRequest.cancel(self.data_request_too_time['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actions_cancel_request_too_time_with_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user1))
        response_action = self.client.post(self.url_action, ActionRequest.cancel(self.data_request_too_time['id']))
        response_action_data = json.loads(response_action.content)
        self.assertEqual(response_action_data['status'], Workday.STATUS_CANCEL)
        self.assertEqual(response_action.status_code, status.HTTP_201_CREATED)

    def test_action_request_with_user_no_line_manger(self):
        self.client.credentials(HTTP_AUTHORIZATION=authentication(self.user4))

        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

        response_action = self.client.post(self.url_action, ActionRequest.reject(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

        response_action = self.client.post(self.url_action, ActionRequest.cancel(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_action_approved_or_rejected_request_by_user(self):
        response_action = self.client.post(self.url_action,
                                           data=ActionRequest.approve(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

        response_action = self.client.post(self.url_action, data=ActionRequest.reject(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_action_approved_request_with_request_canceled(self):
        self.client.post(self.url_action, ActionRequest.cancel(self.response_request_data['id']))

        response_action = self.client.post(self.url_action, ActionRequest.approve(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_action_rejected_request_with_request_canceled(self):
        self.client.post((self.url_action, ActionRequest.cancel(self.response_request_data['id'])))

        response_action = self.client.post(self.url_action, ActionRequest.reject(self.response_request_data['id']))
        self.assertEqual(response_action.status_code, status.HTTP_400_BAD_REQUEST)

    def test_services_approved_with_two_line_manage(self):
        request_detail = ActionRequestService.action_approve(self.response_request_data['id'], self.user2_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.status, Workday.STATUS_APPROVED)
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_FORWARDED)

        request_detail = ActionRequestService.action_approve(self.response_request_data['id'], self.user1_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.status, Workday.STATUS_APPROVED)
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_APPROVED)

    def test_services_approved_with_one_line_manage(self):
        request_detail = ActionRequestService.action_approve(self.request_of_user_4.id, self.user1_profile, '')
        self.assertEqual(request_detail.request_off.id, self.request_of_user_4.id)
        self.assertEqual(request_detail.status, Workday.STATUS_APPROVED)
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_APPROVED)

    def test_services_rejected_and_service_approve_request_approved(self):
        request_detail = ActionRequestService.action_reject(self.response_request_data['id'], self.user2_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.status, Workday.STATUS_REJECTED)
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_REJECTED)

        request_detail = ActionRequestService.action_approve(self.response_request_data['id'], self.user2_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.status, Workday.STATUS_REJECTED)
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_REJECTED)

    def test_services_cancel_and_approve_request_cancel_and_reject_request_cancel(self):
        request_off = ActionRequestService.action_cancel(self.response_request_data['id'], self.user3_profile)
        self.assertEqual(request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_off.status, Workday.STATUS_CANCEL)

        request_detail = ActionRequestService.action_approve(self.response_request_data['id'], self.user2_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_CANCEL)
        self.assertEqual(request_detail.status, None)

        request_detail = ActionRequestService.action_reject(self.response_request_data['id'], self.user2_profile, '')
        self.assertEqual(request_detail.request_off.id, UUID(self.response_request_data['id']))
        self.assertEqual(request_detail.request_off.status, Workday.STATUS_CANCEL)
        self.assertEqual(request_detail.status, None)
