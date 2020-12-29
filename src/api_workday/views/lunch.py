#!/usr/bin/env python

# author Huy
# date 10/23/2019

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_base.services import Utils
from api_base.views import BaseViewSet
from api_user.models import Profile
from api_user.serializers import ProfileName
from api_workday.models import Lunch
from api_workday.serializers import LunchSerializer
from api_workday.services.lunch import LunchService, DateService


class LunchViewSet(BaseViewSet):
    queryset = Lunch.objects.all()
    serializer_class = LunchSerializer
    pagination_class = None
    authentication_classes = (APIAuthentication,)
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = {'list': [IsAdminUser], 'get_lunch_status': [IsAdminUser]}

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        day = DateService.get_date(request.data.get('date'))
        data = LunchService.create_lunch(data, day)
        return Response(data)

    @action(methods=['post'], detail=True)
    def update_lunch_user(self, request, *args, **kwargs):
        data = request.data.copy()
        day = DateService.get_date(request.data.get('date'))
        lunch_id = Utils.convert_to_int(kwargs.get('pk'))
        res, stat = LunchService.update_lunch_for_user(data, day, lunch_id)
        return Response({'response': res}, status=stat)

    def list(self, request, *args, **kwargs):
        lunch_list = LunchService.get_list()
        return Response(lunch_list)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(profile_id=kwargs.get('pk'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        LunchService.delete_lunch(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def get_lunch_status(self, request, *args, **kwargs):
        day = DateService.get_date(request.query_params.get('date'))
        active_profiles = Profile.objects.select_related('user').filter(user__active=True).values('id', 'name')
        for profile in active_profiles:
            profile.update(day=day)
        serializer = ProfileName(active_profiles, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def retrieve_lunch_status(self, request, *args, **kwargs):
        day = DateService.get_date(request.query_params.get('date'))
        instance = Profile.objects.get(id=int(kwargs.get('pk')))
        instance.day = day
        serializer = ProfileName(instance)
        return Response([serializer.data])

    @action(methods=['post'], detail=True)
    def create_user_lunch_month(self, request, *args, **kwargs):
        day = DateService.get_date(request.data.get('date'))
        LunchService.create_user_lunch_month(year=day.year, month=day.month,
                                             lunch_users=Profile.objects.filter(id=kwargs.get('pk')))
        return Response({'success': True})

    @action(methods=['delete'], detail=True)
    def remove_user_lunch_month(self, request, *args, **kwargs):
        profile_id = Utils.convert_to_int(kwargs.get('pk'))
        day = DateService.get_date(request.data.get('date'))
        LunchService.remove_user_lunch_month(day, profile_id)
        return Response({'success': True})

    @action(methods=['post'], detail=True)
    def update_user_lunch_by_days(self, request, *args, **kwargs):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        update_type = request.data.get('type')
        profile_id = Utils.convert_to_int(kwargs.get('pk'))
        LunchService.update_user_lunch_by_days(start_date, end_date, update_type, profile_id)
        return Response({'success': True})
