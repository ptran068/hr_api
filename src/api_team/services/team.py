#!/usr/bin/env python
# author OS
# date 7/25/2019
from django.db.models import Q
from api_base.services import BaseService
from api_user.models import Profile, User
from api_user.serializers.profile import TeamProfile
from api_user.services import UserService
from api_team.models import Team, TeamMembers
from api_user.constants.titles import Titles


class TeamService(BaseService):
    # get all members of a team
    @classmethod
    def get_members_in_team(cls, team_id):
        return list(TeamMembers.objects.filter(team_id=team_id).values_list('member_id', flat=True))

    @classmethod
    def update_line_manager_in_team(cls, team):
        leader = team.team_leader
        project_manager = team.project_manager
        if leader:
            team_members = TeamMembers.objects.filter(team_id=team.id)
            for team_member in team_members:
                member = team_member.member
                if member.profile.line_manager != leader.profile:
                    member.profile.line_manager = leader.profile
                    member.profile.save()
            if project_manager:
                if leader.profile.line_manager != project_manager.profile:
                    leader.profile.line_manager = project_manager.profile
                    leader.profile.save()

    # check this user has a team or not
    @classmethod
    def check_had_team(cls, user_id):
        return bool(TeamMembers.objects.filter(member_id=user_id).first())

    @classmethod
    def check_in_team(cls, user, team_id):
        return bool(TeamMembers.objects.filter(team_id=team_id, member=user).first())

    # check whether pm has team or not
    @classmethod
    def check_owner_team(cls, user, team_id):
        if user.staff:
            return True
        return Team.objects.filter(id=team_id, project_manager_id=user.id)

    # get all teams that current pm has
    @classmethod
    def get_teams_of_project_manager(cls, user_id):
        ret = []
        teams = Team.objects.filter(project_manager_id=user_id)
        for team in teams:
            ret.append(team.id)
        return ret

    # get team of current user
    @classmethod
    def get_team(cls, user_id):
        return list(TeamMembers.objects.filter(member_id=user_id).values_list('team_id', flat=True))

    @classmethod
    def add_new_member(cls, instance, **kwargs):
        user = UserService.get_user_by_email(kwargs.get('email'))
        if user:
            cls.update_user_team(user, instance.id)

    @classmethod
    def remove_member(cls, data, instance):
        user = UserService.get_user_by_email(data.get('email'))
        if user:
            cls._remove_user_team(user, instance.id)
            user.profile.save()

    @classmethod
    def delete_team(cls, team):
        TeamMembers.objects.filter(team_id=team.id).delete()

    @classmethod
    def get_leader(cls, text=None, limit=5):
        if text is None:
            text = ''
        users = User.objects.select_related('profile').filter(profile__name__istartswith=text, staff=0).exclude(title=Titles.TITLES[2][0]). \
                    select_related('leader').filter(leader__team_leader__isnull=True)[:limit]
        return [{
            'id': user.id,
            'email': user.email,
            'name': user.profile.name
        } for user in users]

    @classmethod
    def get_potential_members(cls, instance):
        profiles = Profile.objects.select_related('user').filter(user__active=1).exclude(Q(user__staff=True))
        return [{
            'id': profile.user.id,
            'name': profile.name,
            'email': profile.user.email
        } for profile in profiles if not (cls.check_had_team(profile.user.id) or profile.user.is_project_manager)]

    @classmethod
    def get_profile(cls, data, instance, leaders, project_managers):
        check = True
        data.update(leader_name="No leader")
        if data.get("team_leader"):
            for leader in leaders:
                if cls.leader_accept(data, leader):
                    data.update(leader_name=leader.get("name", "No leader"))
                    check = False
                    break
        if check:
            data.update(team_leader=0)
        if data.get("project_manager"):
            for project_manager in project_managers:
                if cls.project_manager_accept(data, project_manager):
                    data.update(project_manager_name=project_manager.get("name", "No pm"))
                    check = False
                    break
        if check:
            data.update(project_manager=0)
        team_member_ids = cls.get_members_in_team(instance.pk)
        profiles = Profile.objects.filter(user_id__in=team_member_ids)
        for profile in profiles:
            profile.team_leader_id = data.get("team_leader")
            profile.project_manager_id = data.get("project_manager")
        data.update(
            employee_number=profiles.count(),
            employee_list=TeamProfile(profiles, many=True).data,
            non_members=cls.get_potential_members(instance)
        )
        return data

    @classmethod
    def leader_accept(cls, data, leader):
        return data.get("team_leader") == leader.get('user_id') and leader.get('user__active') and \
               cls.check_in_team(leader.get('user_id'), data.get('id'))

    @classmethod
    def project_manager_accept(cls, data, project_manager):
        return data.get("project_manager") == project_manager.get('user_id') and project_manager.get('user__active')

    @classmethod
    def update_user_team(cls, user, team_id):
        team = Team.objects.get(pk=team_id)
        if not cls.check_had_team(user.id) or user.is_project_manager:
            if not cls.check_in_team(user, team_id):
                TeamMembers.objects.create(member=user, team=team)
        else:
            TeamMembers.objects.filter(member=user).update(team=team)
        if team.team_leader and team.team_leader != user:
            user.profile.line_manager = team.team_leader.profile
            user.profile.save()

    @classmethod
    def _remove_user_team(cls, member, team_id):
        TeamMembers.objects.filter(member_id=member.id, team_id=team_id).delete()
        if member.is_project_manager:
            team = Team.objects.filter(id=team_id).first()
            if team:
                team.project_manager = None
                team.save()

    @classmethod
    def set_leader(cls, team, **kwargs):
        email = kwargs.get('email')
        user = UserService.get_user_by_email(email)
        if user:
            team.team_leader = user
            team.save()
            cls.update_line_manager_in_team(team)
            cls.update_user_team(user, team.id)

    @classmethod
    def set_project_manager(cls, team, **kwargs):
        email = kwargs.get('email')
        user = UserService.get_user_by_email(email)
        if user:
            team.project_manager = user
            team.save()
            cls.update_line_manager_in_team(team)
            cls.update_user_team(user, team.id)

    @classmethod
    def move_team(cls, user_id, current_team_id, new_team_id):
        user = User.objects.get(id=user_id)
        cls._remove_user_team(user, current_team_id)
        cls.update_user_team(user, new_team_id)


