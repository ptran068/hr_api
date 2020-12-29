from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_base.services.utils import Utils
from api_base.views import BaseViewSet
from api_user.models.user_education import UserEducation
from api_user.models.user import User
from api_user.serializers.related_profile import UserEducationSerializer
from api_user.permissions import IsAdminOrOwner


class UserEducationViewSet(BaseViewSet):
    serializer_class = UserEducationSerializer
    permission_classes = (IsAdminOrOwner,)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        education = UserEducation.objects.filter(user=user)
        self.check_object_permissions(self.request, education)
        education_serializer = self.get_serializer(education, many=True)
        return Response(education_serializer.data)

    @action(methods=['POST'], detail=True)
    def add(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, user)
        education_serializer = self.get_serializer(data=request.data)
        education_serializer.is_valid(raise_exception=True)
        education_serializer.save(user=user)
        return Response(education_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        education_id = data.get('id')
        if not (education_id and Utils.is_valid_uuid(education_id)):
            data = {'detail': 'invalid education id'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        education = UserEducation.objects.filter(pk=education_id).first()
        self.check_object_permissions(self.request, education)
        education_serializer = self.get_serializer(education, data=request.data, partial=True)
        education_serializer.is_valid(raise_exception=True)
        self.perform_update(education_serializer)
        return Response(education_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        data = request.data.copy()
        education_id = data.get('education_id')
        if not (education_id and Utils.is_valid_uuid(education_id)):
            data = {'detail': 'invalid education id'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        education = UserEducation.objects.filter(pk=education_id).first()
        if education:
            self.check_object_permissions(self.request, education)
            education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
