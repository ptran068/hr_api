#!/usr/bin/env python

# author Huy
# date 8/14/2019

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api_base.serializers import LoginSerializer, InviteSerializer
from api_base.services import LoginService, TokenUtil
from api_user.services import UserService


class LoginViewSet(viewsets.ViewSet):
    permission_classes = []
    authentication_classes = []
    activity_log = True

    @staticmethod
    def create(request):
        login_serializer = LoginSerializer(data=request.data)
        if login_serializer.is_valid(raise_exception=True):
            validated_data = login_serializer.validated_data
            rs = LoginService.login(**validated_data)
            return Response(rs)

    @action(methods=['post'], detail=False)
    def verify(self, request, *args, **kwargs):
        password = request.data.get('password')
        user_data = TokenUtil.verify(request.data.get('token'))
        invite_serializer = InviteSerializer(data=user_data)
        if invite_serializer.is_valid(raise_exception=True):
            email = user_data.get('email')
            user = UserService.get_user_by_email(email)
            if user:
                LoginService.change_password(user, password)
                return Response({'success': True})
        raise ValidationError("Verify error")
