#!/usr/bin/env python

# author Huy
# date 11/26/2019

import datetime

from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_base.services import Utils
from api_base.views import BaseViewSet
from api_workday.constants import Workday
from api_workday.models import ProposeLeave
from api_workday.serializers import ProposeLeaveSerializer
from api_workday.services.propose_leave import ProposeLeaveService


class ProposeLeaveViewSet(BaseViewSet):
    queryset = ProposeLeave.objects.all()
    serializer_class = ProposeLeaveSerializer
    pagination_class = None
    authentication_classes = (APIAuthentication,)
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'reject': [IsAdminUser]}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        profile_id = Utils.convert_to_int(request.data.get('profile'))
        start_date = request.data.get('start')
        end_date = request.data.get('end')
        ProposeLeaveService.approve_finalize(profile_id, start_date, end_date)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = ProposeLeave.objects.filter(start__gte=datetime.datetime.now())
        if request.query_params.get('history'):
            queryset = ProposeLeave.objects.all()
        data = self.get_data(queryset, request.query_params.get('history'))
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        profile_id = Utils.convert_to_int(kwargs.get('pk'))
        queryset = ProposeLeave.objects.filter(start__gte=datetime.datetime.now(), profile_id=profile_id)
        if request.query_params.get('history'):
            queryset = ProposeLeave.objects.filter(start__lt=datetime.datetime.now(), profile_id=profile_id)
        data = self.get_data(queryset, request.query_params.get('history'))
        return Response(data)

    def get_data(self, queryset, history):
        serializer = self.get_serializer(queryset, many=True)
        for data in serializer.data:
            if history and data.get('status') == Workday.STATUS_PENDING:
                data['status'] = Workday.STATUS_PASSED
        return serializer.data

    @action(methods=['put'], detail=True)
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        comments = request.data.get('comments')
        ProposeLeaveService.reject_leave(instance, comments)
        return Response({'success': True})

    @action(methods=['put'], detail=True)
    def withdraw(self, request, *args, **kwargs):
        instance = self.get_object()
        ProposeLeaveService.withdraw_leave(instance)
        return Response({'success': True})

    @action(methods=['get'], detail=False)
    def get_new_leave(self, request, *args, **kwargs):
        count = ProposeLeave.objects.filter(start__gte=datetime.datetime.now(), status='Pending').count()
        return Response({'number': count})
