#! /usr/bin/python
#
# Copyright (C) 2020 paradox.ai
#

__author__ = "huy.tran@paradox.ai"
__date__ = "22/06/2020 09:56"

import datetime

from django.template.loader import render_to_string

from api_base.services import BaseService, GoogleCalendar, SendMail
from api_team.models import Team
from api_user.models import Profile, User
from api_workday.constants import Workday
from api_workday.models import Date


class ProposeLeaveService(BaseService):

    @classmethod
    def approve_finalize(cls, profile_id, start_date, end_date):
        user = Profile.objects.get(id=profile_id)
        email_list = [user.email for user in User.objects.filter(admin=True)]
        subject = 'A new leave from users is proposed'
        content = render_to_string('../templates/admin_leave_email.html',
                                   {'user': user.name,
                                    'date': f'from {start_date} to {end_date}'})
        SendMail.start(email_list, subject, content)

    @classmethod
    def reject_leave(cls, instance, comments):
        instance.status = Workday.STATUS_REJECTED
        instance.comments = comments
        instance.save()

        profile = Profile.objects.get(id=instance.profile_id)
        reason = ''
        if comments:
            reason = f"Reason: {comments}."
        content = render_to_string('../templates/accept_reject_email.html',
                                   {'user': profile.name,
                                    'date': f'from {instance.start} to {instance.end} was ',
                                    'decision': 'rejected. ',
                                    'further': reason})
        SendMail.start([profile.user.email], 'Your leave day was rejected', content)

    @classmethod
    def withdraw_leave(cls, instance):
        if instance.status == Workday.STATUS_ACCEPTED:
            number_of_day = (instance.end - instance.start).days + 1
            f = lambda x: instance.start + datetime.timedelta(days=x)
            dates = [f(i) for i in range(number_of_day) if f(i).weekday() != 5 and f(i).weekday() != 6]
            date_objects = Date.objects.filter(profile_id=instance.profile, date__in=dates)

            user_team = 'No team'
            user = Profile.objects.get(id=instance.profile_id)
            if user.teams:
                team_obj = Team.objects.filter(id=int(user.teams.split(',')[0])).first()
                if team_obj:
                    user_team = team_obj.team_name
            # TODO Remove this once done update Google Calendar
            try:
                items = GoogleCalendar.get()
                GoogleCalendar.delete_event(items, date_objects, user_team)
            except Exception as e:
                print(f"Error with Google Calendar: {str(e)}")
            date_objects.delete()
        instance.delete()
