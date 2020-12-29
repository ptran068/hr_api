from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api_base.views import BaseViewSet
from api_user.models.user_contact import UserContact
from api_user.models.user import User
from api_user.serializers.related_profile import UserContactSerializer
from api_user.permissions import IsAdminOrOwner


class UserContactViewSet(BaseViewSet):
    serializer_class = UserContactSerializer
    permission_classes = (IsAdminOrOwner,)
    permission_classes_by_action = {
        'destroy': [IsAdminUser]
    }

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        contact = UserContact.objects.filter(user=user).first()
        if not contact:
            data = {"detail": "contact information not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, contact)
        contact_serializer = self.get_serializer(contact)
        return Response(contact_serializer.data)

    @action(methods=['POST'], detail=True)
    def add(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, user)
        contact_serializer = self.get_serializer(data=request.data)
        contact_serializer.is_valid(raise_exception=True)
        try:
            contact_serializer.save(user=user)
        except IntegrityError:
            data = {"detail": "User contact information already exist"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(contact_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        contact = UserContact.objects.filter(user=user).first()
        if not contact:
            data = {"detail": "contact information not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, contact)
        contact_serializer = self.get_serializer(contact, data=request.data, partial=True)
        contact_serializer.is_valid(raise_exception=True)
        self.perform_update(contact_serializer)
        return Response(contact_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        UserContact.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
