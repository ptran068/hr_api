from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_base.services.utils import Utils
from api_base.views import BaseViewSet
from api_user.models.user_family_members import UserFamilyMembers
from api_user.models.user import User
from api_user.serializers.related_profile import UserFamilyMembersSerializer
from api_user.permissions import IsAdminOrOwner


class UserFamilyMembersViewSet(BaseViewSet):
    serializer_class = UserFamilyMembersSerializer
    permission_classes = (IsAdminOrOwner,)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        family_members = UserFamilyMembers.objects.filter(user=user)
        self.check_object_permissions(self.request, family_members)
        family_members_serializer = self.get_serializer(family_members, many=True)
        return Response(family_members_serializer.data)

    @action(methods=['POST'], detail=True)
    def add(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, user)
        family_members_serializer = self.get_serializer(data=request.data)
        family_members_serializer.is_valid(raise_exception=True)
        family_members_serializer.save(user=user)
        return Response(family_members_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        family_member_id = data.get('id')
        if not (family_member_id and Utils.is_valid_uuid(family_member_id)):
            data = {'detail': 'invalid family member id'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        family_members = UserFamilyMembers.objects.filter(pk=family_member_id).first()
        self.check_object_permissions(self.request, family_members)
        family_members_serializer = self.get_serializer(family_members, data=request.data, partial=True)
        family_members_serializer.is_valid(raise_exception=True)
        self.perform_update(family_members_serializer)
        return Response(family_members_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        data = request.data.copy()
        family_member_id = data.get('id')
        if not (family_member_id and Utils.is_valid_uuid(family_member_id)):
            data = {'detail': 'invalid family member id'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        family_member = UserFamilyMembers.objects.filter(pk=family_member_id).first()
        if family_member:
            self.check_object_permissions(self.request, family_member)
            family_member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
