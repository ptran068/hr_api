from django.test import TestCase

from api_workday.constants import Workday
from api_workday.factories import DateOffFactory, TypeOffFactory
from api_workday.factories.remain_leave import RemainLeaveFactory
from api_workday.factories.request_off import RequestOffFactory
from api_workday.services.request_off import RequestOffServices
from api_workday.utils.user_auth import UserFactory, ProfileFactory


class RequestOffServiceTest(TestCase):

    def setUp(self):
        self.user1 = UserFactory()
        self.user1_profile = ProfileFactory.create(user=self.user1)

        self.user2 = UserFactory()
        self.user2_profile = ProfileFactory.create(user=self.user2, line_manager=self.user1_profile)

        self.user3 = UserFactory()
        self.user3_profile = ProfileFactory.create(user=self.user3, line_manager=self.user2_profile)

        self.request_off_user1 = RequestOffFactory(profile=self.user1_profile)
        self.request_off_user2_1 = RequestOffFactory(profile=self.user2_profile, status=Workday.STATUS_CANCEL)
        self.request_off_user2_2 = RequestOffFactory(profile=self.user2_profile, status=Workday.STATUS_REJECTED)

        self.date_off_1 = DateOffFactory(request_off=self.request_off_user1)

        self.type_off_company_pay = TypeOffFactory(add_sub_day_off=1)
        self.type_off_insurance_pay = TypeOffFactory(type=1)

        self.remain_leave_user1 = RemainLeaveFactory(profile=self.user1_profile)
        self.remain_leave_user3 = RemainLeaveFactory(profile=self.user3_profile)

        self.valid_data = {
            "date": [{"date": "2026-09-30", "type": "All day", "lunch": "False"},
                     {"date": "2025-09-30", "type": "All day", "lunch": "True"}]
        }

    def test_method_check_overlap_date_output_false(self):
        boolean = RequestOffServices.check_overlap_date(self.valid_data, self.user1_profile.id)
        self.assertFalse(boolean)

    def test_method_check_overlap_date_output_true(self):
        self.date_off_2 = DateOffFactory(request_off=self.request_off_user1, date="2026-09-30")
        boolean = RequestOffServices.check_overlap_date(self.valid_data, self.user1_profile.id)
        self.assertTrue(boolean)

    def test_method_check_overlap_date_without_request_list(self):
        boolean = RequestOffServices.check_overlap_date(self.valid_data, self.user2_profile.id)
        self.assertFalse(boolean)

    def test_method_check_overlap_date_with_request_off_status_cancel_reject(self):
        boolean = RequestOffServices.check_overlap_date(self.valid_data, self.user2_profile.id)
        self.assertFalse(boolean)

    def test_method_check_available_date_off_with_type_off_insurance_pay(self):
        boolean = RequestOffServices.check_available_date_off(self.user2_profile.id, self.type_off_insurance_pay,
                                                              self.valid_data)
        self.assertFalse(boolean)

    def test_method_check_available_date_off_with_type_off_company_pay(self):
        boolean = RequestOffServices.check_available_date_off(self.user1_profile.id, self.type_off_company_pay,
                                                              self.valid_data)
        self.assertFalse(boolean)

    def test_method_check_available_date_off_output_true(self):
        self.date_off_2 = DateOffFactory(request_off=self.request_off_user1, date="2026-09-30")
        boolean = RequestOffServices.check_available_date_off(self.user1_profile.id, self.type_off_company_pay,
                                                              self.valid_data)
        self.assertTrue(boolean)

    def test_method_check_available_date_off_output_false(self):
        valid_data = {
            "date": [{"date": "2026-09-30", "type": "All day", "lunch": "False"}]}
        boolean = RequestOffServices.check_available_date_off(self.user1_profile.id, self.type_off_company_pay,
                                                              valid_data)
        self.assertFalse(boolean)

    def test_method_check_available_date_off_without_request_list(self):
        boolean = RequestOffServices.check_available_date_off(self.user3_profile.id, self.type_off_company_pay,
                                                              self.valid_data)
        self.assertFalse(boolean)

    def test_method_check_available_date_off_with_many_date_input(self):
        valid_data = {
            "date": [{"date": "2026-10-30", "type": "All day", "lunch": "False"},
                     {"date": "2025-11-30", "type": "All day", "lunch": "True"},
                     {"date": "2025-09-30", "type": "All day", "lunch": "True"}]
        }
        boolean = RequestOffServices.check_available_date_off(self.user3_profile.id, self.type_off_company_pay,
                                                              valid_data)
        self.assertFalse(boolean)
