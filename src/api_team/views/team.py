from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from api_base.services import Utils
from api_base.views import BaseViewSet
from api_team.models import Team, TeamMembers
from api_team.serializers import TeamSerializers, MemberSerializer
from api_team.services import TeamService
from api_team.permissions import IsProjectManager
from api_user.models import Profile, User


class TeamViewSet(BaseViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializers
    pagination_class = None
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'add_member': [IsAdminUser | IsProjectManager],
        'remove_member': [IsAdminUser | IsProjectManager],
        'set_leader': [IsAdminUser | IsProjectManager],
    }

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        if not request_data.get('team_leader'):
            data = {'detail': 'Please choose team leader'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        leader = User.objects.filter(email=request_data['team_leader']).first()
        if not leader:
            data = {'detail': 'User not found'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        request_data['team_leader'] = leader.id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        query_option = request.query_params.get('limit')
        if query_option:
            queryset = Team.objects.values('team_name').distinct()
            return Response(dict(data=queryset))
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        TeamService.delete_team(instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def send_leader(self, request, *args, **kwargs):
        text = request.query_params.get('name')
        leaders = TeamService.get_leader(text=text, limit=5)
        return Response(leaders)

    @action(methods=['put'], detail=True)
    def add_member(self, request, *args, **kwargs):
        # pms are not allowed to modify members of non owner teams
        if not TeamService.check_owner_team(request.user, kwargs.get('pk')):
            data = {"detail": "You do not have permission to modify this team"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        data = request.data.copy()
        if data.get('emails'):
            for email in data.get('emails').split(','):
                data.update(email=email)
                member_serializer = MemberSerializer(data=data)
                if member_serializer.is_valid(raise_exception=True):
                    validate_data = member_serializer.validated_data
                    if validate_data.get('email'):
                        TeamService.add_new_member(instance, **validate_data)
        return Response({'Success': True})

    @action(methods=['put'], detail=True)
    def remove_member(self, request, *args, **kwargs):
        # pms are not allowed to modify members of non owner teams
        if not TeamService.check_owner_team(request.user, kwargs.get('pk')):
            data = {"detail": "You do not have permission to modify this team"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validate_data = serializer.validated_data
            TeamService.remove_member(validate_data, instance)
        return Response({'Success': True})

    @action(methods=['put'], detail=True)
    def set_leader(self, request, *args, **kwargs):
        # pms are not allowed to modify members of non owner teams
        if not TeamService.check_owner_team(request.user, kwargs.get('pk')):
            data = {"detail": "You do not have permission to modify this team"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        team = self.get_object()
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validate_data = serializer.validated_data
            try:
                TeamService.set_leader(team, **validate_data)
            except IntegrityError:
                data = {"detail": "This user is already leader of another team"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            return Response({'Success': True})

    @action(methods=['get'], detail=True)
    def get_new_teams(self, request, *args, **kwargs):
        instance = User.objects.get(id=kwargs.get('pk'))
        queryset = Team.objects.exclude(team__member_id=instance.id).select_related()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['put'], detail=False)
    def move_team(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        current_team_id = Utils.convert_to_int(request.data.get('current_team_id'))
        new_team_id = Utils.convert_to_int(request.data.get('new_team_id'))
        TeamService.move_team(user_id, current_team_id, new_team_id)
        return Response({'Success': True})

    @action(methods=['put'], detail=True)
    def set_project_manager(self, request, *args, **kwargs):
        team = self.get_object()
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validate_data = serializer.validated_data
            TeamService.set_project_manager(team, **validate_data)
            return Response({'Success': True})
