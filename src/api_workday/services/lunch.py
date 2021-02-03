#!/usr/bin/env python

# author Huy
# date 12/8/2019

import calendar
import datetime

from django.db.models import F
from lunarcalendar import Converter, Solar
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api_base.services import BaseService, Utils
from api_user.models import Profile
from api_workday.models import Lunch, Lunchdate
from api_workday.serializers import LunchSerializer
from api_workday.services.date import DateService


class LunchService(BaseService):

    @classmethod
    def get_list(cls):
        response = []
        now = datetime.datetime.now()
        next_year, next_month = Utils.nextmonth(year=now.year, month=now.month)
        for date in Lunchdate.objects.filter(date__month__in=[now.month, next_month]):
            queryset = Lunch.objects.filter(date=date.id).annotate(name=F('profile__name')).values('profile', 'name')
            profiles = Profile.objects.filter(user__active=True).exclude(
                id__in=[data.get('profile') for data in queryset]).values('id', 'name')
            response.extend(({'start': date.date, 'end': date.date, 'title': 'Eat', 'class': 'eat',
                              'content': str(queryset.count()), 'reason': queryset},
                             {'start': date.date, 'end': date.date, 'title': 'No eat', 'class': 'no',
                              'content': str(profiles.count()), 'reason': profiles}))
        return response

    @classmethod
    def create_lunch(cls, data, day):
        cls.check_order_time(day, datetime.datetime.now())
        try:
            lunch_date = Lunchdate.objects.get(date=day)
        except Lunchdate.DoesNotExist:
            lunch_date = Lunchdate.objects.create(date=day)
        data.update(date=lunch_date.id)
        serializer = LunchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @classmethod
    def update_lunch_for_user(cls, data, day, lunch_id):
        if Lunchdate.objects.filter(date=day).exists():
            lunch_date = Lunchdate.objects.get(date=day)
            if Lunch.objects.filter(profile=lunch_id, date=lunch_date).exists():
                instance = Lunch.objects.get(profile=lunch_id, date=lunch_date)
                cls.check_order_time(instance.date.date, datetime.datetime.now())
                instance.delete()
                stat = status.HTTP_204_NO_CONTENT
                rs = 'Removed successfully'
            else:
                cls.create_lunch(data, day)
                stat = status.HTTP_201_CREATED
                rs = 'Created successfully'
        else:
            cls.create_lunch(data, day)
            stat = status.HTTP_201_CREATED
            rs = 'Created successfully'
        return rs, stat

    @classmethod
    def update_lunch(cls, profile):
        now = datetime.datetime.now()
        Lunch.objects.filter(profile_id=profile.id, date__date__gt=datetime.datetime.now()).delete()
        cls.create_lunch_days(year=now.year, month=now.month, lunch_users=[profile])
        year, next_month = Utils.nextmonth(year=now.year, month=now.month)
        cls.create_lunch_days(year=year, month=next_month, lunch_users=[profile])

    @classmethod
    def delete_lunch(cls, lunch):
        now = datetime.datetime.now()
        day = lunch.date.date
        cls.check_order_time(day, now)
        lunch.delete()

    @classmethod
    def create_lunch_days(cls, month, year, lunch_users):
        if Lunchdate.objects.filter(date__year=year, date__month=month).count() < 28:
            num_days = calendar.monthrange(year, month)[1]
            days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
            objs = [Lunchdate(date=day) for day in days if day.weekday() != 5 and day.weekday() != 6
                    and not Lunchdate.objects.filter(date=day).exists()]
            Lunchdate.objects.bulk_create(objs)
            now = datetime.datetime.now()
            if now.hour >= 10:
                lunch_days = Lunchdate.objects.filter(date__month=month, date__gt=now)
            else:
                lunch_days = Lunchdate.objects.filter(date__month=month, date__gte=now)
            lunch_objs = [Lunch(profile=user, date=day) for user in lunch_users for day in lunch_days
                          if user.lunch_weekly and day.date.weekday() in list(map(int, user.lunch_weekly.split(',')))
                          and not Lunch.objects.filter(profile=user, date=day).exists()]
            Lunch.objects.bulk_create(lunch_objs)
            cls.update_lunar_month()

    @classmethod
    def update_lunar_month(cls):
        now = datetime.datetime.now()
        for date in Lunchdate.objects.filter(date__gte=now):
            solar = Solar(date.date.year, date.date.month, date.date.day)
            lunar = Converter.Solar2Lunar(solar)
            if lunar.day == 1 or lunar.day == 15:
                date.veggie = True
                date.save()

    @classmethod
    def create_user_lunch_month(cls, month, year, lunch_users):
        if Lunchdate.objects.filter(date__year=year, date__month=month).count() < 28:
            num_days = calendar.monthrange(year, month)[1]
            days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
            objs = [Lunchdate(date=day) for day in days if day.weekday() != 5 and day.weekday() != 6
                    and not Lunchdate.objects.filter(date=day).exists()]
            Lunchdate.objects.bulk_create(objs)
            now = datetime.datetime.now()
            if now.hour >= 10:
                lunch_days = Lunchdate.objects.filter(date__month=month, date__gt=now)
            else:
                lunch_days = Lunchdate.objects.filter(date__month=month, date__gte=now)
            lunch_objs = [Lunch(profile=user, date=day) for user in lunch_users for day in lunch_days
                          if not Lunch.objects.filter(profile=user, date=day).exists()]
            Lunch.objects.bulk_create(lunch_objs)

    @classmethod
    def remove_user_lunch_month(cls, day, profile_id):
        lunch_days = [date.id for date in Lunchdate.objects.filter(date__month=day.month, date__year=day.year)]
        Lunch.objects.filter(profile=profile_id, date__in=lunch_days).delete()

    @classmethod
    def update_user_lunch_by_days(cls, start_date, end_date, update_type, profile_id):
        now = datetime.datetime.now()
        start_date = DateService.get_date(start_date)
        end_date = DateService.get_date(end_date)
        number_of_day = (end_date - start_date).days + 1
        f = lambda x: start_date + datetime.timedelta(days=x)  # Get day range
        if now.hour >= 10:
            dates = [f(i) for i in range(number_of_day) if
                     f(i).weekday() != 5 and f(i).weekday() != 6 and f(i) > now.date()]
        else:
            dates = [f(i) for i in range(number_of_day) if
                     f(i).weekday() != 5 and f(i).weekday() != 6 and f(i) >= now.date()]
        if update_type == 'Remove':
            Lunch.objects.filter(profile_id=profile_id, date__date__in=dates).delete()
        else:
            lunch_objs = [Lunch(profile=Profile.objects.get(id=profile_id), date=Lunchdate.objects.get(date=day))
                          for day in dates if not Lunch.objects.filter(profile_id=profile_id, date__date=day).exists()]
            Lunch.objects.bulk_create(lunch_objs)

    @classmethod
    def get_lunch_day_in_week(cls, date):
        now = datetime.datetime.now()
        day = DateService.get_date(date)
        if day.date() < now.date() or (day.date() == now.date() and now.hour >= 10):
            days = [day + datetime.timedelta(days=i) for i in range(1, 6 - day.weekday() + 1)]
        else:
            days = [day + datetime.timedelta(days=i) for i in range(0, 6 - day.weekday() + 1)]
        return days

    @classmethod
    def check_order_time(cls, day, now):
        if day < now.date() or (day == now.date() and now.hour >= 10):
            raise ValidationError('Lunch order time is over.')
