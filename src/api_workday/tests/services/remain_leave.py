import datetime
from django.test import TestCase
from rest_framework.exceptions import ValidationError, ErrorDetail
from api_workday.factories.remain_leave import RemainLeaveFactory
from api_workday.services.remain_leave import RemainLeaveService
from api_workday.utils.user_auth import UserFactory, ProfileFactory
from api_workday.models.remain_leave import RemainLeave
from api_workday.factories.company import CompanyFactory
class RemainLeaveServiceTest(TestCase):
    def setUp(self):
        self.admin = UserFactory()
        self.admin_profile = ProfileFactory.create(user=self.admin, join_date=datetime.date(2020, 10, 12))
        self.user1 = UserFactory(staff=False)
        self.profile1 = ProfileFactory.create(user=self.user1, join_date=datetime.date(2020, 10, 12))
        self.user2 = UserFactory(staff=False)
        self.profile2 = ProfileFactory.create(user=self.user2, join_date=datetime.date(2020, 10, 12))
        self.user3 = UserFactory(staff=False)
        self.profile3 = ProfileFactory.create(user=self.user3, join_date=datetime.date(2020, 10, 12))
        CompanyFactory(month_remove_annual_leave_last_year=11)
        self.valid_data = {
            "date": [{"date": "2026-09-30", "type": "All day", "lunch": "False"},
                     {"date": "2025-09-30", "type": "All day", "lunch": "True"}]
        }
        self.list_profile = [self.profile1, self.profile2, self.profile3]
        RemainLeaveFactory(profile=self.profile1, year=2019, annual_leave=12, current_days_off=5)
        RemainLeaveFactory(profile=self.profile1, year=2020, annual_leave=3, current_days_off=3,
                           annual_leave_last_year=5)
        RemainLeaveFactory(profile=self.profile1, year=2021, annual_leave=12, current_days_off=12,
                           annual_leave_last_year=0)
    def test_method_create_annual_leave(self):
        expected_results = {
            "annual_leave": 3,
            "current_days_off": 3,
        }
        RemainLeaveService.create_annual_leave(year=2020, profile=self.profile2)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile2.id, year=2020).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile2.id, year=2020).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_update_annual_leave(self):
        join_date = "2019-10-15"
        expected_results = {
            "annual_leave": 12,
            "current_days_off": 12,
        }
        RemainLeaveService.update_annual_leave(join_date, self.profile1)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_add_annual_leave_last_year_for_next_year(self):
        expected_results = {
            "annual_leave": 12,
            "current_days_off": 12,
            "annual_leave_last_year": 3
        }
        RemainLeaveService.add_annual_leave_last_year_for_next_year()
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_add_annual_leave_last_year_has_date_off_next_year(self):
        expected_results = {
            "annual_leave": 13,
            "current_days_off": 11,
            "annual_leave_last_year": 0
        }
        RemainLeaveFactory(profile=self.profile2, year=2021, annual_leave=13, current_days_off=10,
                           annual_leave_last_year=5)
        RemainLeaveFactory(profile=self.profile2, year=2020, annual_leave=12, current_days_off=1)
        RemainLeaveService.add_annual_leave_last_year_for_next_year()
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile2.id, year=2021).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile2.id, year=2021).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile2.id, year=2021).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_get_annual_leave_by_year(self):
        response = RemainLeaveService.get_annual_leave_by_year(2020)
        self.assertEqual(len(response), len(RemainLeave.objects.filter(year=2020)))
    def test_method_handle_annual_leave_sub_annual_last_year(self):
        expected_results = {
            "annual_leave": 3,
            "current_days_off": 3,
            "annual_leave_last_year": 2
        }
        RemainLeaveService.handle_annual_leave(self.profile1, 3, True)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).current_days_off,
                         expected_results.get('current_days_off'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
    def test_method_handle_annual_leave_sub_annual_last_year_with_day_leave_greater_annual_leave_last_year(self):
        expected_results = {
            "annual_leave": 3,
            "current_days_off": 2,
            "annual_leave_last_year": 0
        }
        RemainLeaveService.handle_annual_leave(self.profile1, 6, True)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).current_days_off,
                         expected_results.get('current_days_off'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
    def test_method_handle_annual_leave_not_sub_annual_last_year(self):
        expected_results = {
            "annual_leave": 3,
            "current_days_off": 0,
            "annual_leave_last_year": 5
        }
        RemainLeaveService.handle_annual_leave(self.profile1, 3)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).current_days_off,
                         expected_results.get('current_days_off'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
    def test_method_handle_annual_leave_next_year(self):
        expected_results = {
            "annual_leave": 12,
            "current_days_off": 9,
        }
        RemainLeaveService.handle_annual_leave_next_year(self.profile1, 3)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_handle_annual_leave_next_year_with_day_leave_greater_leave_days(self):
        expected_results = {
            "annual_leave": 12,
            "current_days_off": 12,
        }
        with self.assertRaises(ValidationError) as cm:
            RemainLeaveService.handle_annual_leave_next_year(self.profile1, 15)
        the_exception = cm.exception
        self.assertEqual(the_exception.detail, {'status': ErrorDetail(string='The number of days off is not enough',
                                                                      code='invalid')})
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).annual_leave,
                         expected_results.get('annual_leave'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2021).current_days_off,
                         expected_results.get('current_days_off'))
    def test_method_handle_annual_leave_last_year(self):
        expected_results = {
            "current_days_off": 2,
            "annual_leave_last_year": 2,
        }
        RemainLeaveService.handle_annual_leave_last_year(self.profile1, 3)
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2019).current_days_off,
                         expected_results.get('current_days_off'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
    def test_method_handle_annual_leave_last_year_with_day_leave_greater_leave_days(self):
        expected_results = {
            "current_days_off": 5,
            "annual_leave_last_year": 5,
        }
        with self.assertRaises(ValidationError) as cm:
            RemainLeaveService.handle_annual_leave_last_year(self.profile1, 6)
        the_exception = cm.exception
        self.assertEqual(the_exception.detail, {'status': ErrorDetail(string='The number of days off is not enough',
                                                                      code='invalid')})
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2019).current_days_off,
                         expected_results.get('current_days_off'))
        self.assertEqual(RemainLeave.objects.get(profile_id=self.profile1.id, year=2020).annual_leave_last_year,
                         expected_results.get('annual_leave_last_year'))
    def test_method_add_bonus(self):
        expected_results = {
            "profile_id": str(self.profile1.id),
            "bonus": 3,
            "current_days_off": 6
        }
        response = RemainLeaveService.add_bonus(self.profile1, 3)
        self.assertEqual(response.data.get('profile').get('id'), expected_results.get('profile_id'))
        self.assertEqual(response.data.get('bonus'), expected_results.get('bonus'))
        self.assertEqual(response.data.get('current_days_off'), expected_results.get('current_days_off'))
