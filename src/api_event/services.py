from functools import reduce
from django.db.models import Q
from django.http import QueryDict

from api_user.models import Profile
from datetime import timedelta
from .models import Event
import datetime
from django.conf import settings
from utils.get_admins import get_all_admins
from slack import WebClient
from slack.errors import SlackApiError
import operator
import calendar

Client = WebClient(token=settings.BOT_USER_ACCESS_TOKEN)


class EventServices:

    @classmethod
    def get_birthday_events(cls):
        today = datetime.date.today()
        date_instance = datetime.date(today.year, today.month, today.day).strftime('%Y-%m-%d')
        channel = settings.CHANNEL
        events = Event.objects.filter(date=date_instance)
        if not events:
            return []
        try:
            for event in events:
                Client.files_upload(
                    channels=channel,
                    file=event.image.path,
                    initial_comment=event.wishes + ' ' + '@' + event.profile.name
                )
        except SlackApiError as e:
            raise Exception(e)
        return

    @classmethod
    def reminder_admin_set_birthday_slack(cls):
        today = datetime.date.today()
        start_week = today - datetime.timedelta(today.weekday())
        month_number = calendar.monthrange(start_week.year, start_week.month)[-1]
        end_week = start_week + datetime.timedelta(6)
        date_instance = datetime.date(today.year, today.month, today.day).strftime('%Y-%m-%d')
        profile_ids = Event.objects.filter(date=date_instance).values_list('profile_id', flat=True)
        link_set_event = settings.LINK_EVENT_SYSTEM
        exclude_args = dict()
        profiles = Profile.objects.filter(Q(birth_day__month=start_week.month) | Q(birth_day__month=end_week.month))
        if end_week.day < start_week.day:
            range_less = [start_week.day, month_number + 1]
            range_greate = [1, end_week.day + 1]
            profiles = profiles.filter(Q(birth_day__day__range=range_less) | Q(birth_day__day__range=range_greate))
        else:
            profiles = profiles.filter(Q(birth_day__day__range=[start_week.day, end_week.day]))

        if profile_ids:
            exclude_args = dict(id__in=profile_ids)
        profiles = profiles.exclude(**exclude_args)

        if not profiles.exists():
            raise Exception('Have no birthday')
        list_admins = get_all_admins()
        text = 'We have {} birthday events in this month what have not setted.Please access to link {} to set up these events.Thanks'.format(
            len(profiles), link_set_event)
        try:
            for admin in list_admins:
                Client.chat_postMessage(
                    channel=admin.profile.slack_id,
                    text=text,
                )
        except SlackApiError as e:
            raise Exception(e)
        return

    @classmethod
    def get_birthdays_today(cls):
        today = datetime.date.today()
        users = Profile.objects.filter(birth_day=today)
        if not users.exists():
            raise Exception('Have no birthday in today')
        return users

    @classmethod
    def get_birthdays_in_month(cls, month):
        month = month if month else datetime.date.today().month
        users = Profile.objects.filter(birth_day__month=month)
        if not users.exists():
            raise Exception('Have no birthday in month')
        return users

    @classmethod
    def create(cls, serializer, data):
        today = datetime.date.today()
        is_send_to_all = data.get('is_send_to_all')
        month = data.get('month')
        if is_send_to_all:
            list_users = cls.get_birthdays_in_month(month)
            list_birthdays = []
            for user in list_users:
                birthday = Event.objects.filter(profile=user, date=today)
                if birthday:
                    continue
                list_birthdays.append(Event(
                    date=today,
                    profile=user,
                    image=serializer.validated_data['image'],
                    wishes=serializer.validated_data['wishes']
                ))
            return Event.objects.bulk_create(list_birthdays)
        birthday = Event.objects.filter(profile_id=data.get('profile'))
        if birthday:
            raise Exception('Birthday was setted')
        return serializer.save(date=today, profile_id=data.get('profile'))
