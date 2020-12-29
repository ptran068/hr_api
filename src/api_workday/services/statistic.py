import datetime

from django.db.models import Q

from api_base.services import BaseService
from api_workday.constants import Workday
from api_workday.models import RemainLeave
from api_workday.models.date_off import DateOff
from api_workday.serializers.date_off import DateOffSerizlizer
from api_workday.serializers.profile_detail import ProfileDetailSerizlizer


class StatisticServices(BaseService):

    @classmethod
    def get_business_days(cls, month, year):
        holidays = {datetime.date(year, 9, 2)}
        business_days = 0
        for i in range(Workday.FIRST_DAY + 1, Workday.LAST_DAY + 1):
            try:
                this_date = datetime.date(year, month, i)
            except(ValueError):
                break
            if this_date.weekday() < 5 and this_date not in holidays:
                business_days += 1
        return business_days

    @classmethod
    def get_the_number_of_days_off(cls, list_date_off):
        date_leave = 0
        for date_off in list_date_off:
            if date_off.get('type') == Workday.FULL:
                date_leave += 1
            else:
                date_leave += 0.5
        return date_leave

    @classmethod
    def get_list_date_off_detail_for_profile(cls, month, date_off_full):
        date_off_in_month = date_off_full.filter(date__month=month)
        serializer_date = DateOffSerizlizer(date_off_in_month, many=True)
        list_date_off = [{'date': date.get('date'),
                          'type': date.get('type'),
                          'lunch': date.get('lunch'),
                          'type_off_title': date.get('request_off').get('type_title'),
                          'type_off_type': date.get('request_off').get('type_type'),
                          'type_off_is_ot_days': date.get('request_off').get('type_is_ot_days'),
                          'type_off_is_paid_salary': date.get('request_off').get('type_is_paid_salary'),
                          'type_off_add_sub_day_off': date.get('request_off').get('type_add_sub_day_off')}
                         for date in serializer_date.data]
        leave_days = []
        ot_days = []
        night_days = []
        remote_days = []
        insurance_days = []
        unpaid_days = []
        for detail_date_off in list_date_off:
            if detail_date_off.get('type_off_add_sub_day_off') == 1:
                leave_days.append(detail_date_off)
            elif detail_date_off.get('type_off_is_ot_days') == 1:
                ot_days.append(detail_date_off)
            elif detail_date_off.get('type_off_is_ot_days') == 2 and detail_date_off.get('type_off_type') == 0:
                night_days.append(detail_date_off)
            elif not detail_date_off.get('type_off_is_paid_salary'):
                unpaid_days.append(detail_date_off)
            elif detail_date_off.get('type_off_type') == 1:
                insurance_days.append(detail_date_off)
            else:
                remote_days.append(detail_date_off)
        return {'leave_days': leave_days,
                'ot_days': ot_days,
                'night_days': night_days,
                'remote_days': remote_days,
                'insurance_days': insurance_days,
                'unpaid_days': unpaid_days}

    @classmethod
    def get_date_off_for_statistic_admin(cls, name, email, month, year, profile):
        data = []
        try:
            year = int(year)
            month = int(month)
        except:
            return data
        if name is not None:
            profile = profile.filter(Q(name__icontains=name))
        if email is not None:
            profile = profile.filter(Q(user__email__icontains=email))
        if year > datetime.datetime.now().year or month > Workday.LAST_MONTH:
            return data
        for profile_id in profile:
            if year in range(profile_id.join_date.year, datetime.datetime.now().year + 1):
                if year == profile_id.join_date.year:
                    date_off_full_in_year = DateOff.objects.filter(request_off__status=Workday.STATUS_APPROVED,
                                                                   request_off__profile=profile_id,
                                                                   date__year=year)
                    if month >= profile_id.join_date.month:
                        detail = cls.get_list_date_off_detail_for_profile(month, date_off_full_in_year)
                    else:
                        continue
                else:
                    date_off_full_in_year = DateOff.objects.filter(request_off__status=Workday.STATUS_APPROVED,
                                                                   request_off__profile=profile_id,
                                                                   date__year=year)
                    detail = cls.get_list_date_off_detail_for_profile(month, date_off_full_in_year)
                serializer_profile = ProfileDetailSerizlizer(profile_id)
                remain = RemainLeave.objects.filter(profile=profile_id, year=year).first()
                if remain is None:
                    continue
                working_days = cls.get_business_days(month, year) - \
                               cls.get_the_number_of_days_off(detail.get('leave_days')) - \
                               cls.get_the_number_of_days_off(detail.get('insurance_days')) - \
                               cls.get_the_number_of_days_off(detail.get('unpaid_days'))
                profile_date = {
                    'id': profile_id.id,
                    'name': profile_id.name,
                    'email': serializer_profile.data.get('user').get('email'),
                    'annual_leave': remain.annual_leave,
                    'leave_days_number': cls.get_the_number_of_days_off(detail.get('leave_days')),
                    'leave_days': detail.get('leave_days'),
                    'OT_days_number': cls.get_the_number_of_days_off(detail.get('ot_days')),
                    'OT_days': detail.get('ot_days'),
                    'night_days_number': cls.get_the_number_of_days_off(detail.get('night_days')),
                    'night_days': detail.get('night_days'),
                    'remote_days_number': cls.get_the_number_of_days_off(detail.get('remote_days')),
                    'remote_days': detail.get('remote_days'),
                    'insurance_days_number': cls.get_the_number_of_days_off(detail.get('insurance_days')),
                    'insurance_days': detail.get('insurance_days'),
                    'unpaid_days_number': cls.get_the_number_of_days_off(detail.get('unpaid_days')),
                    'unpaid_days': detail.get('unpaid_days'),
                    'working_days': working_days,
                    'current_days_off': remain.current_days_off,
                    'annual_leave_last_year': remain.annual_leave_last_year
                }
                data.append(profile_date)
            else:
                continue
        return data

    @classmethod
    def get_date_off_for_statistic_user(cls, year, profile):
        data = []
        try:
            year = int(year)
        except:
            return data
        if year not in range(profile.join_date.year, datetime.datetime.now().year + 1):
            return data
        start_month = Workday.FIRST_MONTH + 1
        if year == profile.join_date.year:
            start_month = profile.join_date.month
        date_off_full_in_year = DateOff.objects.filter(request_off__status=Workday.STATUS_APPROVED,
                                                       request_off__profile=profile,
                                                       date__year=year)
        remain = RemainLeave.objects.filter(profile=profile, year=year).first()
        if remain is None:
            return data
        for month in range(start_month, Workday.LAST_MONTH + 1):
            detail = cls.get_list_date_off_detail_for_profile(month, date_off_full_in_year)
            working_days = cls.get_business_days(month, year) - \
                           cls.get_the_number_of_days_off(detail.get('leave_days')) - \
                           cls.get_the_number_of_days_off(detail.get('insurance_days')) - \
                           cls.get_the_number_of_days_off(detail.get('unpaid_days'))
            profile_date = {
                'month': month,
                'annual_leave': remain.annual_leave,
                'leave_days_number': cls.get_the_number_of_days_off(detail.get('leave_days')),
                'leave_days': detail.get('leave_days'),
                'OT_days_number': cls.get_the_number_of_days_off(detail.get('ot_days')),
                'OT_days': detail.get('ot_days'),
                'night_days_number': cls.get_the_number_of_days_off(detail.get('night_days')),
                'night_days': detail.get('night_days'),
                'remote_days_number': cls.get_the_number_of_days_off(detail.get('remote_days')),
                'remote_days': detail.get('remote_days'),
                'insurance_days_number': cls.get_the_number_of_days_off(detail.get('insurance_days')),
                'insurance_days': detail.get('insurance_days'),
                'unpaid_days_number': cls.get_the_number_of_days_off(detail.get('unpaid_days')),
                'unpaid_days': detail.get('unpaid_days'),
                'working_days': working_days,
                'current_days_off': remain.current_days_off,
                'annual_leave_last_year': remain.annual_leave_last_year,
                'join_date': profile.join_date
            }
            data.append(profile_date)
        return data
