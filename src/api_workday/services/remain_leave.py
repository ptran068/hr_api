import math
import datetime
from api_company.models import Company
from api_workday.models.date_off import DateOff
from api_base.services import BaseService
from api_workday.serializers.remain_leave import RemainLeaveSerializer
from api_workday.models.remain_leave import RemainLeave
from api_workday.constants.date import Workday
from rest_framework import serializers
from api_workday.services.date_off import DateOffService


class RemainLeaveService(BaseService):

    @classmethod
    def update_annual_leave(cls, join_date, profile):
        year = datetime.datetime.now().year
        date_object = datetime.datetime.strptime(join_date, "%Y-%m-%d")
        remain_leave = RemainLeave.objects.filter(profile_id=profile.id, year=year).first()
        if remain_leave is None:
            cls.create_annual_leave(year=year, profile=profile)
            remain_leave = RemainLeave.objects.get_remain_leave_by_profile_id(profile.id)

        off_number = remain_leave.bonus + remain_leave.annual_leave - remain_leave.current_days_off
        timestamp = datetime.date(datetime.datetime.now().year, Workday.LAST_MONTH, Workday.LAST_DAY)
        new_annual_leave = cls.get_annual_leave(last_date=timestamp, join_date=date_object)
        remain_leave.annual_leave = new_annual_leave
        remain_leave.current_days_off = new_annual_leave + remain_leave.bonus - off_number
        remain_leave.save()

    @classmethod
    def add_annual_leave_last_year_for_next_year(cls):
        # cron job call 31/12
        for remain_leave_next_year in RemainLeave.objects.filter(year=datetime.datetime.now().year + 1):
            number_day_off_of_next_year = remain_leave_next_year.annual_leave - remain_leave_next_year.current_days_off
            present_annual_leave = RemainLeave.objects.filter(profile_id=remain_leave_next_year.profile.id,
                                                              year=datetime.datetime.now().year).first()
            num_add_leave_next_year = present_annual_leave.current_days_off - number_day_off_of_next_year
            if present_annual_leave.current_days_off >= number_day_off_of_next_year:
                remain_leave_next_year.current_days_off = remain_leave_next_year.annual_leave
                remain_leave_next_year.annual_leave_last_year = num_add_leave_next_year
            else:
                remain_leave_next_year.annual_leave_last_year = 0
                remain_leave_next_year.current_days_off = remain_leave_next_year.annual_leave + num_add_leave_next_year
            remain_leave_next_year.save()

    @classmethod
    def create_annual_leave(cls, **kwargs):
        timestamp = datetime.date(kwargs.get('year'), Workday.LAST_MONTH, Workday.LAST_DAY)
        profile = kwargs.get('profile')
        data = {
            "annual_leave": cls.get_annual_leave(timestamp, profile.join_date),
            "current_days_off": cls.get_annual_leave(timestamp, profile.join_date),
            "year": timestamp.year
        }
        serializer = RemainLeaveSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save(profile=profile)
        return data

    @classmethod
    def get_annual_leave_by_year(cls, year):
        annual_leaves = RemainLeave.objects.filter(year=year)
        serializer = RemainLeaveSerializer(annual_leaves, many=True)
        return serializer.data

    @classmethod
    def handle_annual_leave(cls, profile, day_leave, is_annual_leave_last_year=False):
        remain_leave = RemainLeave.objects.get_remain_leave_by_profile_id(id=profile.id)
        if is_annual_leave_last_year:
            if remain_leave.current_days_off + remain_leave.annual_leave_last_year - day_leave < 0:
                raise serializers.ValidationError({'status': Workday.STT_NUM_NOT_ENOUGH})
            if remain_leave.annual_leave_last_year < day_leave:
                remain_leave.current_days_off -= day_leave - remain_leave.annual_leave_last_year
                remain_leave.annual_leave_last_year = 0
            else:
                remain_leave.annual_leave_last_year -= day_leave
        else:
            if remain_leave.current_days_off < day_leave:
                raise serializers.ValidationError({'status': Workday.STT_NUM_NOT_ENOUGH})
            remain_leave.current_days_off -= day_leave
        remain_leave.save()
        return RemainLeaveSerializer(remain_leave)

    @classmethod
    def handle_annual_leave_next_year(cls, profile, day_leave):
        remain_leave = RemainLeave.objects.get_remain_leave_next_year_by_profile_id(id=profile.id)
        if remain_leave.current_days_off - day_leave < 0:
            raise serializers.ValidationError({'status': Workday.STT_NUM_NOT_ENOUGH})
        remain_leave.current_days_off -= day_leave
        remain_leave.save()
        return RemainLeaveSerializer(remain_leave)

    @classmethod
    def handle_annual_leave_last_year(cls, profile, day_leave):
        remain_leave_last_year = RemainLeave.objects.get_remain_leave_last_year_by_profile_id(id=profile.id)
        remain_leave_present = RemainLeave.objects.get_remain_leave_by_profile_id(id=profile.id)

        if remain_leave_last_year.current_days_off < day_leave:
            raise serializers.ValidationError({'status': Workday.STT_NUM_NOT_ENOUGH})
        remain_leave_last_year.current_days_off -= day_leave
        remain_leave_present.annual_leave_last_year -= day_leave
        if remain_leave_present.annual_leave_last_year < 0:
            remain_leave_present.current_days_off += remain_leave_present.annual_leave_last_year
            remain_leave_present.annual_leave_last_year = 0
        remain_leave_last_year.save()
        remain_leave_present.save()

    @classmethod
    def add_bonus(cls, profile, bonus):
        remain_leave = RemainLeave.objects.get_remain_leave_by_profile_id(id=profile.id)
        remain_leave.current_days_off += bonus
        remain_leave.bonus += bonus
        remain_leave.save()
        return RemainLeaveSerializer(remain_leave)

    @classmethod
    def get_annual_leave(cls, last_date, join_date):
        join_date = datetime.date(join_date.year, join_date.month, join_date.day)
        if math.floor((last_date - join_date).days / 365) == 0:
            return round((last_date - join_date).days / 365 * 12)
        else:
            return 12 + math.floor((last_date - join_date).days / 365 - 1)

    @classmethod
    def get_next_year(cls):
        list_year = RemainLeave.objects.values_list('year', flat=True)
        if len(list_year) == 0:
            return datetime.datetime.now().year
        return max(list_year) + 1

    @classmethod
    def get_unconfirmed_days(cls, list_request_off_unconfirmed):
        company_setting = Company.objects.all().first()
        if not company_setting:
            return Exception('Company setting not found')
        month_annual_leave_last_year = company_setting.expired_annual_leave_last_year
        list_date_unconfirmed = []
        for request_off in list_request_off_unconfirmed:
            list_date_unconfirmed += DateOff.objects.filter(request_off_id=request_off.id,
                                                            request_off__type_off__add_sub_day_off=1)


        list_date_sub_annual_leave_last_year = list(
            filter(lambda date_off: date_off.date.month < month_annual_leave_last_year, list_date_unconfirmed))
        list_date_not_sub_annual_leave_last_year = list(
            filter(lambda date_off: date_off.date.month >= month_annual_leave_last_year, list_date_unconfirmed))

        unconfirmed_days_sub_annual_leave_last_year = DateOffService.get_num_days_off_by_list_date(
            list_date_sub_annual_leave_last_year)
        unconfirmed_days_not_sub_annual_leave_last_year = DateOffService.get_num_days_off_by_list_date(
            list_date_not_sub_annual_leave_last_year)

        return unconfirmed_days_sub_annual_leave_last_year, unconfirmed_days_not_sub_annual_leave_last_year
