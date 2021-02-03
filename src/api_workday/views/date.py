#!/usr/bin/env python

# author Huy
# date 9/7/2019

from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_base.services import GoogleCalendar, Utils
from api_base.views import BaseViewSet
from api_user.models import Profile
from api_workday.constants import Workday
from api_workday.models import Date
from api_workday.serializers import DateSerializer
from api_workday.services.date import DateService


class DateViewSet(BaseViewSet):
    queryset = Date.objects.filter(date__year=datetime.now().year)
    serializer_class = DateSerializer
    pagination_class = None
    authentication_classes = (APIAuthentication,)
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = {'create': [IsAdminUser], 'list_date_statistic': [IsAdminUser]}

    def create(self, request, *args, **kwargs):
        dates, user_name, user_team, rs = DateService.get_creation_data(request.data)
        profile_id = request.data.get('profile')
        for date in dates:
            data = DateService.get_individual_data(request.data.copy(), user_name, date, dates)
            if self.queryset.filter(date=date, profile_id=request.data.get('profile')).count():
                existed_date = Date.objects.get(date=date, profile_id=profile_id)
                DateService.duplicate_date(existed_date, data, Workday.MORNING, user_team)
                DateService.duplicate_date(existed_date, data, Workday.AFTERNOON, user_team)
            else:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                rs.append(serializer.data)

                # TODO Remove this once done update Google Calendar
                try:
                    GoogleCalendar.create_event(data, user_team)
                except Exception as e:
                    print(f"Error with Google Calendar: {str(e)}")
                have_lunch = request.data.get('lunch')
                DateService.update_lunch(profile_id, date, have_lunch)
        leave_day_left = DateService.get_leave_day_statistic(profile_id).get('leave_day_left')
        res = dict(
            success=True,
            result=rs,
            leave_day_left=leave_day_left
        )
        return Response(res, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile_id=kwargs.get('pk'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def list_date_statistic(self, request, *args, **kwargs):
        active_profiles = Profile.objects.filter(user__active=True)
        rs = list((DateService.get_leave_day_statistic(profile.id) for profile in active_profiles))
        return Response(rs)

    @action(methods=['get'], detail=True)
    def retrieve_date_statistic(self, request, *args, **kwargs):
        profile_id = Utils.convert_to_int(kwargs.get('pk'))
        return Response(DateService.get_leave_day_statistic(profile_id))

    @action(methods=['get'], detail=False)
    def get_today(self, request, *args, **kwargs):
        leave = Date.objects.filter(date=datetime.now(), title=Workday.LEAVE).count()
        remote = Date.objects.filter(date=datetime.now(), title=Workday.REMOTE).count()
        return Response({'leave': leave,
                         'remote': remote})
