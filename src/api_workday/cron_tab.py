import datetime
from django.conf import settings
from slack import WebClient
from slack.errors import SlackApiError
from api_workday.models.date_off import DateOff
from api_workday.constants.date import Workday
from api_workday.models.type_off import TypeOff

Client = WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
from api_user.models import Profile
from .services.remain_leave import RemainLeaveService


def create_remain_leave_for_next_year():
    next_year = RemainLeaveService.get_next_year()
    if next_year == datetime.datetime.now().year + 1:
        for profile in Profile.objects.all():
            RemainLeaveService.create_annual_leave(year=next_year, profile=profile)


def add_annual_leave_last_year_for_next_year():
    return RemainLeaveService.add_annual_leave_last_year_for_next_year()




def get_leave_today():
    today = datetime.date.today()
    date_instance = datetime.date(today.year, today.month, today.day).strftime('%Y-%m-%d')
    channel = settings.CHANNEL_LEAVE_NOTICE
    date_offs = DateOff.objects.filter(date=date_instance, request_off__status=Workday.STATUS_APPROVED)

    if date_offs:
        type_offs = TypeOff.objects.all()
        text = 'Update employee situation today:\n'
        for type_off in type_offs:
            date_offs_by_type = list(filter(lambda date_off: date_off.request_off.type_off == type_off, date_offs))
            if date_offs_by_type:
                text += content_notice(date_offs_by_type, type_off.title)

        try:
            Client.chat_postMessage(
                channel=channel,
                text=text
            )
            return
        except SlackApiError as e:
            raise Exception(e)


def content_notice(date_offs, type_title):
    list_name = [date_off.request_off.profile.name + f'({date_off.type})' for date_off in date_offs]
    name_text = '\n• '.join(list_name)
    text = f'+ {type_title}:\n' + f'\n```• {name_text}```\n'
    return text

