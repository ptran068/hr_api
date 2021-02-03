import datetime

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.authentications import APIAuthentication
from api_company.models import Company
from api_user.models.profile import Profile
from api_workday.constants import Workday
from api_workday.models.request_off import RequestOff
from api_workday.models import RequestOff
from rest_framework.response import Response
from api_workday.models.remain_leave import RemainLeave
from api_workday.serializers.remain_leave import RemainLeaveSerializer
from rest_framework import status
from api_base.views import BaseViewSet
from api_workday.services.remain_leave import RemainLeaveService


class RemainLeaveViewSet(BaseViewSet):
    authentication_classes = (APIAuthentication,)
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'retrieve': [IsAuthenticated]}

    def create(self, request, *args, **kwargs):
        next_year = RemainLeaveService.get_next_year()
        if next_year == datetime.datetime.now().year + 1 and not RemainLeave.objects.filter(year=next_year).exists():
            with transaction.atomic():
                for profile in Profile.objects.all():
                    RemainLeaveService.create_annual_leave(year=next_year, profile=profile)
                return Response(RemainLeaveService.get_annual_leave_by_year(next_year), status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Year has been used'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        year = RemainLeaveService.get_next_year()
        if RemainLeave.objects.filter(year=kwargs.get('year') | year).exists():
            return Response(RemainLeaveService.get_annual_leave_by_year(year=kwargs.get('year') | year))
        else:
            return Response({'status': 'Year has been used'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        company_setting = Company.objects.all().first()
        if company_setting is None:
            return Response({'status': 'Company setting not found'}, status=status.HTTP_400_BAD_REQUEST)

        profile = request.user.profile
        remain_leave = RemainLeave.objects.get_remain_leave_by_profile_id(id=profile.id)
        request_off_unconfirmed = RequestOff.objects.filter(
            status__in=[Workday.STATUS_FORWARDED, Workday.STATUS_PENDING], profile_id=profile.id)
        serializer = RemainLeaveSerializer(remain_leave)
        sub_leave_last_year, sub_annual_leave = RemainLeaveService.get_unconfirmed_days(request_off_unconfirmed)

        current_days_off = serializer.data.get('current_days_off') - sub_annual_leave
        annual_leave_last_year = serializer.data.get(
            'annual_leave_last_year') - sub_leave_last_year
        if annual_leave_last_year < 0:
            current_days_off += current_days_off
            annual_leave_last_year = 0

        response = {
            'current_days_off': current_days_off,
            'annual_leave_last_year': annual_leave_last_year,
            'profile': serializer.data.get('profile'),
            'month': company_setting.expired_annual_leave_last_year
        }
        return Response(response)

