from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api_base.views import BaseViewSet
from api_user.models.user_identity import UserIdentity
from api_user.models.user import User
from api_user.serializers.related_profile import UserIdentitySerializer
from api_user.permissions import IsAdminOrOwner


class UserIdentityViewSet(BaseViewSet):
    serializer_class = UserIdentitySerializer
    permission_classes = (IsAdminOrOwner,)
    permission_classes_by_action = {
        'destroy': [IsAdminUser]
    }

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        identity = UserIdentity.objects.filter(user=user).first()
        if not identity:
            data = {"detail": "User identity information not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, identity)
        identity_serializer = self.get_serializer(identity)
        return Response(identity_serializer.data)

    @action(methods=['POST'], detail=True)
    def add(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, user)
        identity_serializer = self.get_serializer(data=request.data)
        identity_serializer.is_valid(raise_exception=True)
        try:
            identity_serializer.save(user=user)
        except IntegrityError:
            data = {"detail": "User identity already exist"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(identity_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        identity = UserIdentity.objects.filter(user=user).first()
        if not identity:
            data = {"detail": "User identity information not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, identity)
        identity_serializer = self.get_serializer(identity, data=request.data, partial=True)
        identity_serializer.is_valid(raise_exception=True)
        self.perform_update(identity_serializer)
        return Response(identity_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        UserIdentity.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
