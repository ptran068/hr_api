import datetime

from api_base.services import BaseService
from api_company.models import Company
from api_user.models.profile import Profile
from api_workday.constants import Workday
from api_workday.models.date_off import DateOff
from api_workday.models.remain_leave import RemainLeave
from api_workday.models.request_off import RequestOff


class RequestOffServices(BaseService):

    @classmethod
    def check_overlap_date(cls, data, profile_id):
        status = [Workday.STATUS_REJECTED, Workday.STATUS_CANCEL]
        list_id_request = RequestOff.objects.filter(profile_id=profile_id).exclude(status__in=status). \
            values_list('id', flat=True)
        if not list_id_request:
            return False
        for id_request in list_id_request:
            for date in data["date"]:
                date_off = DateOff.objects.filter(date=date['date']).filter(request_off_id=id_request)
                if date_off.exists():
                    return True
        return False

    @classmethod
    def check_out_of_join_date(cls, data, profile_id):
        profile = Profile.objects.filter(id=profile_id).first()
        if profile:
            for date_off in data['date']:
                date_time_obj = datetime.datetime.strptime(date_off['date'], '%Y-%m-%d').date()
                if date_time_obj < profile.join_date:
                    return True
        return False

    @classmethod
    def get_expired_annual_leave_last_year_in_company_settings(cls):
        company = Company.objects.all().first()
        if company:
            return company.expired_annual_leave_last_year
        return 7

    @classmethod
    def get_the_number_of_days_off(cls, list_date_off):
        date_leave = 0
        for date_off in list(list_date_off):
            try:
                if date_off["type"] == Workday.FULL:
                    date_leave += 1
                else:
                    date_leave += 0.5
            except:
                if date_off.type == Workday.FULL:
                    date_leave += 1
                else:
                    date_leave += 0.5
        return date_leave

    @classmethod
    def get_list_date_off_by_year(cls, data):
        now = datetime.datetime.now().year
        month_check = cls.get_expired_annual_leave_last_year_in_company_settings()
        list_date_leave_last_year_after_month_reset = []
        list_date_leave_last_year = []
        list_date_leave_current_year_after_month_reset = []
        list_date_leave_current_year = []
        list_date_leave_next_year_after_month_reset = []
        list_date_leave_next_year = []
        for date_off in data['date']:
            date_time_obj = datetime.datetime.strptime(date_off['date'], '%Y-%m-%d').date()
            if date_time_obj.year == now + 1:
                list_date_leave_next_year.append(date_off)
                if date_time_obj.month >= month_check:
                    list_date_leave_next_year_after_month_reset.append(date_off)
            if date_time_obj.year == now:
                list_date_leave_current_year.append(date_off)
                if date_time_obj.month >= month_check:
                    list_date_leave_current_year_after_month_reset.append(date_off)
            if date_time_obj.year == now - 1:
                list_date_leave_last_year.append(date_off)
                if date_time_obj.month >= month_check:
                    list_date_leave_last_year_after_month_reset.append(date_off)
        return {
            "last_year": list_date_leave_last_year,
            "current_year": list_date_leave_current_year,
            "next_year": list_date_leave_next_year,
            "last_year_month": list_date_leave_last_year_after_month_reset,
            "current_year_month": list_date_leave_current_year_after_month_reset,
            "next_year_month": list_date_leave_next_year_after_month_reset}

    @classmethod
    def get_list_date_left_by_year(cls, list_id_request):
        now = datetime.datetime.now().year
        month_check = cls.get_expired_annual_leave_last_year_in_company_settings()
        list_date = DateOff.objects.filter(request_off__in=list_id_request)
        list_date_off_last_year = list_date.filter(date__year=now - 1)
        list_date_off_last_year_after_month_reset = list_date_off_last_year.filter(date__month__gte=month_check)
        list_date_off_current_year = list_date.filter(date__year=now)
        list_date_off_current_year_after_month_reset = list_date_off_current_year.filter(date__month__gte=month_check)
        list_date_off_next_year = list_date.filter(date__year=now + 1)
        list_date_off_next_year_after_month_reset = list_date_off_next_year.filter(date__month__gte=month_check)
        return {
            "last_year": list_date_off_last_year,
            "current_year": list_date_off_current_year,
            "next_year": list_date_off_next_year,
            "last_year_month": list_date_off_last_year_after_month_reset,
            "current_year_month": list_date_off_current_year_after_month_reset,
            "next_year_month": list_date_off_next_year_after_month_reset}

    @classmethod
    def check_date_off_with_remain_leave(cls, total_date, total_date_after, year, profile_id):
        remain = RemainLeave.objects.filter(profile=profile_id, year=year).first()
        if remain:
            if total_date_after > remain.current_days_off:
                return True
            if total_date > remain.current_days_off + remain.annual_leave_last_year:
                return True
        return False

    @classmethod
    def check_available_date_off(cls, profile_id, type_off, data):
        if type_off.add_sub_day_off != Workday.ANNUAL_LEAVE:
            return False
        now = datetime.datetime.now().year
        status = [Workday.STATUS_PENDING, Workday.STATUS_FORWARDED]
        list_id_request = RequestOff.objects.filter(profile_id=profile_id, status__in=status)

        date_off = cls.get_list_date_left_by_year(list_id_request)

        list_date_off_last_year = date_off.get('last_year')
        list_date_off_current_year = date_off.get('current_year')
        list_date_off_next_year = date_off.get('next_year')
        list_date_off_last_year_after_month_reset = date_off.get('last_year_month')
        list_date_off_current_year_after_month_reset = date_off.get('current_year_month')
        list_date_off_next_year_after_month_reset = date_off.get('next_year_month')

        date_leave = cls.get_list_date_off_by_year(data)

        list_date_leave_last_year = date_leave.get('last_year')
        list_date_leave_current_year = date_leave.get('current_year')
        list_date_leave_next_year = date_leave.get('next_year')
        list_date_leave_last_year_after_month_reset = date_leave.get('last_year_month')
        list_date_leave_current_year_after_month_reset = date_leave.get('current_year_month')
        list_date_leave_next_year_after_month_reset = date_leave.get('next_year_month')

        total_date_last_year = cls.get_the_number_of_days_off(list_date_off_last_year) + \
            cls.get_the_number_of_days_off(list_date_leave_last_year)

        total_date_current_year = cls.get_the_number_of_days_off(list_date_off_current_year) + \
            cls.get_the_number_of_days_off(list_date_leave_current_year)

        total_date_next_year = cls.get_the_number_of_days_off(list_date_off_next_year) + \
            cls.get_the_number_of_days_off(list_date_leave_next_year)

        total_date_last_year_after_month_reset = cls.get_the_number_of_days_off(
            list_date_off_last_year_after_month_reset) + \
            cls.get_the_number_of_days_off(list_date_leave_last_year_after_month_reset)

        total_date_current_year_after_month_reset = cls.get_the_number_of_days_off(
            list_date_off_current_year_after_month_reset) + \
            cls.get_the_number_of_days_off(list_date_leave_current_year_after_month_reset)

        total_date_next_year_after_month_reset = cls.get_the_number_of_days_off(
            list_date_off_next_year_after_month_reset) + \
            cls.get_the_number_of_days_off(list_date_leave_next_year_after_month_reset)

        if cls.check_date_off_with_remain_leave(total_date_last_year, total_date_last_year_after_month_reset, now-1,
                                                profile_id):
            return True
        if cls.check_date_off_with_remain_leave(total_date_current_year, total_date_current_year_after_month_reset, now,
                                                profile_id):
            return True
        if cls.check_date_off_with_remain_leave(total_date_next_year, total_date_next_year_after_month_reset, now+1,
                                                profile_id):
            return True
        return False
