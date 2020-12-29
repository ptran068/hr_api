from rest_framework import serializers

from api_team.models import Team
from api_team.services import TeamService
from api_user.models import Profile


class TeamSerializers(serializers.ModelSerializer):

    def create(self, validated_data):
        team = Team.objects.create(**validated_data)
        TeamService.update_user_team(validated_data.get('team_leader'), team.id)
        return team

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        leaders = Profile.objects.select_related('user').filter(user_id=instance.team_leader).values('user_id', 'user__active', 'teams', 'name')
        project_managers = Profile.objects.select_related('user').filter(user_id=instance.project_manager).values('user_id', 'user__active', 'teams', 'name')
        ret = TeamService.get_profile(ret, instance, leaders, project_managers)
        return ret

    class Meta:
        model = Team
        fields = '__all__'


class MemberSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField(max_length=255)
