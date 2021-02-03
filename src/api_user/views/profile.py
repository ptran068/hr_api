from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api_base.views import BaseViewSet
from api_user.models.profile import Profile
from api_user.serializers import ProfileLunch, ProfileSerializers
from api_lunch.services import LunchServices
from api_workday.services.remain_leave import RemainLeaveService


class ProfileViewSet(BaseViewSet):
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializers
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'destroy': [IsAdminUser]}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.email = instance.user.email
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = Profile.objects.filter(user__id=request.data.get('user')).first()
        with transaction.atomic():
            RemainLeaveService.update_annual_leave(request.data.get('join_date'), profile)
            self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def update_lunch(self, request, *args, **kwargs):
        # TODO Create a service/update validate for ProfileLunch for this
        data = request.data.copy()
        # TODO Check UI again for all this, after update, remove below codes
        # FIXME lunch_weekly need to remove ',' as first character
        # FIXME lunch and veggie param need to be 0/1 instead
        lunch_weekly = data.get('lunch_weekly')
        if lunch_weekly == 'null':
            lunch_weekly = None
        elif lunch_weekly.startswith(','):
            lunch_weekly = lunch_weekly[1:]
        data.update(
            lunch_weekly=lunch_weekly,
            lunch=True if data.get('check') == 'true' else False,
            veggie=True if data.get('veggie') == 'true' else False,
        )
        # TODO Remove to here

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProfileLunch(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        LunchServices.update_lunch(instance)

        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True)
    def get_profile_lunch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProfileLunch(instance)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def set_line_manager(self, request, *args, **kwargs):
        data = request.data.copy()
        manager_name = data.get('name')
        manager_profile = self.queryset.filter(name=manager_name).first()
        if not manager_profile:
            data = {'detail': 'Profile of this user not found'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        current_user = get_object_or_404(Profile, pk=kwargs.get('pk'))
        if current_user.id == manager_profile.id:
            data = {'detail': 'Can not assign manager by itself'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if current_user == manager_profile.line_manager:
            data = {'detail': 'You are manager of this user'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        current_user.line_manager = manager_profile
        current_user.save()
        data = { 'manager_id': manager_profile.user.id }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def set_level_approved(self, request, *args, **kwargs):
        data = request.data.copy()
        level = data.get('level')
        current_profile = self.queryset.filter(pk=kwargs.get('pk')).first()
        if not current_profile:
            data = {'detail': 'User not found'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        current_profile.maximum_level_approved = level
        current_profile.save()
        data = {'level': current_profile.maximum_level_approved}
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=True, permission_classes=[IsAdminUser])
    def remove_line_manager(self, request, *args, **kwargs):
        current_user = get_object_or_404(Profile, pk=kwargs.get('pk'))
        current_user.line_manager = None
        current_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
