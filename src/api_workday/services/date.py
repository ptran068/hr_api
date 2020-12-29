#!/usr/bin/env python

# author Huy
# date 9/19/2019

import datetime

from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string

from api_base.services import BaseService, GoogleCalendar, SendMail, Utils
from api_team.models import Team
from api_user.models import Profile
from api_workday.constants import Workday
from api_workday.models import ProposeLeave, Lunch, Lunchdate, Date


class DateService(BaseService):

    @classmethod
    def get_date(cls, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d').date()

    @classmethod
    def get_creation_data(cls, data):
        proposed = ProposeLeave.objects.get(id=int(data.get('id')))
        proposed.status = Workday.STATUS_ACCEPTED
        proposed.save()

        start_date = cls.get_date(data.get('start'))
        end_date = cls.get_date(data.get('end'))
        profile = Profile.objects.get(id=data.get("profile"))

        content = render_to_string('../templates/accept_reject_email.html',
                                   {'user': profile.name,
                                    'date': f'from {start_date} to {end_date} was ',
                                    'decision': 'accepted.',
                                    'further': ''})
        SendMail.start([profile.user.email], 'Your leave day was accepted', content)

        user_team = 'No team'
        if profile.teams:
            team = Team.objects.filter(id=int(profile.teams.split(',')[0])).first()
            if team:
                user_team = team.team_name

        """Get weekdays, exclude Saturday and Sunday"""
        number_of_day = (end_date - start_date).days + 1
        f = lambda x: start_date + datetime.timedelta(days=x)
        dates = [f(i) for i in range(number_of_day) if f(i).weekday() != 5 and f(i).weekday() != 6]
        return dates, profile.name, user_team, []

    @classmethod
    def get_individual_data(cls, data, user_name, date, dates):
        data['date'] = date
        start_time = data.get('start_hour')
        end_time = data.get('end_hour')
        start_hour = int(data.get('start_hour')[:2])
        end_hour = int(data.get('end_hour')[:2])
        if len(dates) == 1:
            data['content'] = f'{user_name} ({start_time} - {end_time})'
            data['type'] = {
                True: Workday.MORNING,
                False: {
                    True: Workday.AFTERNOON,
                    False: Workday.FULL
                }[start_hour >= 12]
            }[end_hour <= 13 and start_hour <= 13]
        else:
            if dates.index(date) == 0:
                data['content'] = f'{Profile.objects.get(id=data.get("profile")).name} ({start_time} - 17:30)'
                data['type'] = {
                    True: Workday.FULL,
                    False: Workday.AFTERNOON
                }[start_hour < 12]
            elif dates.index(date) == len(dates) - 1:
                data['content'] = f'{Profile.objects.get(id=data.get("profile")).name} (08:00 - {end_time})'
                data['type'] = {
                    True: Workday.FULL,
                    False: Workday.MORNING
                }[end_hour > 13]
            else:
                data['content'] = f'{Profile.objects.get(id=data.get("profile")).name} (08:00 - 17:30)'
                data['type'] = Workday.FULL
        return data

    @classmethod
    def update_lunch(cls, profile_id, date, have_lunch):
        lunch = Lunch.objects.filter(profile_id=profile_id, date__date=date).first()
        if have_lunch == 'No' and lunch:
            lunch.delete()
        if have_lunch == 'Yes' and not lunch:
            lunch_date = Lunchdate.objects.filter(date=date).first()
            if lunch_date:
                if not Lunch.objects.filter(profile_id=profile_id, date=lunch_date).exists():
                    Lunch.objects.create(profile_id=profile_id, date=lunch_date)
            else:
                lunch_date = Lunchdate.objects.create(date=date)
                Lunch.objects.create(profile_id=profile_id, date=lunch_date)

    @classmethod
    def duplicate_date(cls, day, data, key, user_team):
        if day.type == key and data.get('type') != key:
            day.type = Workday.FULL
            old_content = day.content
            new_content = {
                Workday.MORNING: f"{' '.join(data.get('content').split()[0:-3])} (8:00 - {data.get('end_hour')})",
                Workday.AFTERNOON: f"{' '.join(data.get('content').split()[0:-3])} ({data.get('start_hour')} - 17:30)"
            }.get(key)
            day.content = new_content
            day.save()
            # TODO Remove this once done update Google Calendar
            try:
                GoogleCalendar.update_event(data, old_content, new_content, user_team)
            except Exception as e:
                print(f"Error with Google Calendar: {str(e)}")

    @classmethod
    def get_leave_day_statistic(cls, profile_id):
        now = datetime.datetime.now()
        user_profile = Profile.objects.get(id=profile_id)

        last_year_queryset = Date.objects.filter(date__year=now.year - 1)
        last_remote, last_half_leave, last_full_leave = cls.get_leave_remote(last_year_queryset, profile_id)
        last_total_leave = last_full_leave + last_half_leave * 0.5

        first_half_queryset = Date.objects.filter(date__year=now.year, date__month__lt=7)
        first_half_remote, first_half_half_leave, first_half_full_leave = cls.get_leave_remote(
            first_half_queryset,
            profile_id)
        first_half_total_leave = first_half_full_leave + first_half_half_leave * 0.5

        last_leave_day_left = cls.get_leave_day_in_year(last_total_leave, user_profile.join_date)
        if user_profile.join_date.month < 7:
            last_leave_day_left -= 1

        if now.month < 7:
            if last_leave_day_left > 0:
                current_leave_day_left = cls.get_leave_day_in_year(first_half_total_leave,
                                                                   user_profile.join_date)
                leave_day_left = f"{last_leave_day_left} days last year, {current_leave_day_left} days this year"
            else:
                current_leave_day_left = cls.get_leave_day_in_year(first_half_total_leave,
                                                                   user_profile.join_date) + last_leave_day_left
                leave_day_left = f"{current_leave_day_left} days"
            total_leave = Utils.convert_to_int(first_half_total_leave)
            total_remote = first_half_remote
        else:
            second_half_queryset = Date.objects.filter(date__year=now.year, date__month__gte=7)
            second_half_remote, second_half_half_leave, second_half_full_leave = cls.get_leave_remote(
                second_half_queryset,
                profile_id)
            second_half_total_leave = second_half_full_leave + second_half_half_leave * 0.5
            if last_leave_day_left > 0:

                current_leave_day_left = cls.get_leave_day_in_year(second_half_total_leave,
                                                                   user_profile.join_date)
            else:
                current_leave_day_left = cls.get_leave_day_in_year(second_half_total_leave,
                                                                   user_profile.join_date) + last_leave_day_left
            leave_day_left = f"{current_leave_day_left} days"
            total_leave = Utils.convert_to_int(first_half_total_leave + second_half_total_leave)
            total_remote = first_half_remote + second_half_remote
        return {'id': profile_id,
                'name': user_profile.name,
                'leave_day_number': f'{total_leave} leave, {total_remote} remote',
                'leave_day_left': leave_day_left}

    @classmethod
    def get_leave_remote(cls, queryset, profile_id):
        remote = queryset.filter(profile_id=profile_id, title=Workday.REMOTE).count()
        leave = queryset.filter(profile_id=profile_id, title=Workday.LEAVE)
        half_leave_day = leave.exclude(type=Workday.FULL).count()
        full_leave_day = leave.filter(type=Workday.FULL).count()
        return remote, half_leave_day, full_leave_day

    @classmethod
    def get_leave_day_in_year(cls, total_leave, join_date):
        leave_day_left = Utils.convert_to_int(12 - total_leave + relativedelta(datetime.datetime.now(), join_date).years)
        return leave_day_left
