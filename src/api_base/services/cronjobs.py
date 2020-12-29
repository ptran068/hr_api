#! /usr/bin/python
#
# Copyright (C) 2020 paradox.ai
#

__author__ = "huy.tran@paradox.ai"
__date__ = "11/06/2020 11:53"

import datetime

import requests
from django.conf import settings

from api_base.services import Utils
from api_user.models import Profile
from api_workday.constants import Workday
from api_workday.models import Date, Lunch
from api_workday.services import LunchService


def leave_notify():
    leave = Date.objects.filter(date=datetime.datetime.now(), title=Workday.LEAVE)
    leave_profiles = [date.profile_id for date in leave]
    leave_names = [profile.name for profile in Profile.objects.filter(id__in=leave_profiles)]
    leave_text = '\n• '.join(leave_names)

    remote = Date.objects.filter(date=datetime.datetime.now(), title=Workday.REMOTE)
    remote_profiles = [date.profile_id for date in remote]
    remote_names = [profile.name for profile in Profile.objects.filter(id__in=remote_profiles)]
    remote_text = '\n• '.join(remote_names)

    if leave_names and remote_names:
        text = f'There is *_{len(leave_names)}_* people leave today:\n```• {leave_text}```\n' \
               f'And *_{len(remote_names)}_* people working remote today:\n```• {remote_text}```'
    elif leave_names:
        text = f'There is *_{len(leave_names)}_* people leave today:\n```• {leave_text}```'
    elif remote_names:
        text = f'There is *_{len(remote_names)}_* people working remote today:\n ```• {remote_text}```'
    else:
        text = 'No one leave today'
    url = settings.LEAVE_NOTIFICATION_SLACK_API
    data = {'text': text}
    requests.post(url, json=data)


def lunch_notify():
    lunch_count = Lunch.objects.filter(date__date=datetime.datetime.now().date()).count()
    url = settings.LUNCH_NOTIFICATION_SLACK_API
    data = {'text': f'There is {lunch_count} people having lunch at company today.'}
    requests.post(url, json=data)


def lunch_creation():
    current_month, current_year = Utils.get_current_date()
    year, next_month = Utils.nextmonth(year=current_year, month=current_month)
    LunchService.create_lunch_days(next_month, year, lunch_users=Profile.objects.filter(lunch=True))
