from api_base.services import BaseService
from api_workday.models.date_off import DateOff
from api_workday.constants.date import Workday
from api_workday.serializers import DateOffForCalendarSerializer


class CalendarServices(BaseService):

    @classmethod
    def get_lay_days_by_profile(cls, profile):
        days_off = DateOff.objects.filter(request_off__status=Workday.STATUS_APPROVED, request_off__profile=profile)
        list_dates = DateOffForCalendarSerializer(days_off, many=True).data
        data = [
            {
                'id': date_off.get('id'),
                'date': date_off.get('date'),
                'type': date_off.get('type'),
                'request_off': date_off.get('request_off'),
                'name': profile.name,
                'email': profile.user.email,
                'lunch': date_off.get('lunch')
            } for date_off in list_dates]
        return data

