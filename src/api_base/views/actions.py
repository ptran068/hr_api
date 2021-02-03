#!/usr/bin/env python

# author Huy
# date 12/8/2019

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api_base.services import TokenUtil, Utils, LoginService
from api_user.models import Profile
from api_workday.services.lunch import LunchService


class ActionViewSet(viewsets.ViewSet):
    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def forgot_password(self, request, *args, **kwargs):
        email = request.data.get('email')
        success = LoginService.forgot_password(email)
        if success:
            return Response({"success": True})
        raise ValidationError("User does not exists")

    @action(methods=['put'], detail=False , permission_classes=[AllowAny])
    def change_password(self, request, *args, **kwargs):
        user = TokenUtil.decode(request.data.get('token'), 1)
        password = request.data.get('password')
        LoginService.change_password(user, password)
        return Response({"success": True})

    @action(methods=['post'], detail=False)
    def create_lunch_current_month(self, request, *args, **kwargs):
        current_month, current_year = Utils.get_current_date()
        LunchService.create_lunch_days(current_month, current_year, lunch_users=Profile.objects.filter(lunch=True))
        return Response({'success': True})
