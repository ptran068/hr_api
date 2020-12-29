from django.conf import settings
from rest_framework import serializers
from api_team.models import Team
from api_user.models import Profile, User
from api_user.serializers import PhotoSerializer
from api_workday.models import Lunch


class ProfileSerializers(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    admin = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    line_manager_email = serializers.EmailField(required=False)
    line_manager_user_id = serializers.EmailField(required=False)
    photo = PhotoSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(active=instance.user.active)
        # restrict access to other profile
        request = self.context.get("request")
        access_user = request.user
        if not (access_user.is_staff or access_user.id == instance.user.id):
            ret = {key: value for key, value in ret.items() if key in ['name', 'phone', 'birth_day']}
            birth_day = ret.get('birth_day')
            if birth_day:
                ymd = birth_day.split('-')
                ret.update(birth_day=f'{ymd[1]}-{ymd[2]}')
            return ret
        # Get line manager email
        manager = User.objects.filter(profile__id=ret.get('line_manager')).first()
        if manager:
            ret.update(line_manager_email=manager.email)
            ret.update(line_manager_user_id=manager.id)
        # Get team for each user
        teams = []
        team_queryset = Team.objects.filter(team__member_id=instance.user.id).select_related()
        if team_queryset:
            for team in team_queryset:
                teams.append({
                    'id': team.id,
                    'name': team and team.team_name or ''
                })
        ret.update(teams=teams)
        return ret

    def validate_join_date(self, value):
        request = self.context.get("request")
        access_user = request.user
        if not access_user.is_admin:
            return self.instance.join_date
        return value

    def update(self, instance, validated_data):
        if validated_data.get('join_date') is None:
            validated_data.pop('join_date')
        profile = super().update(instance, validated_data)
        email = validated_data.get('email')
        title = validated_data.get('title')
        admin = validated_data.get('admin')
        request = self.context.get("request")
        access_user = request.user
        if email:
            if access_user.is_admin:
                if admin == 'true':
                    profile.user.staff = True
                else:
                    profile.user.staff = False
                profile.user.title = title
            profile.user.email = email
            profile.user.save()
        return profile


class ProfileName(serializers.ModelSerializer):
    day = serializers.DateField(required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        lunch_day = ret.get('day')
        lunch_objs = Lunch.objects.filter(date__date=lunch_day)
        lunch_profile_ids = list(lunch.profile_id for lunch in lunch_objs)
        if ret.get('id') in lunch_profile_ids:
            try:
                _lunch = lunch_objs.get(profile_id=ret.get('id'))
                ret.update(
                    lunch_id=_lunch.id,
                    status='Lunch'
                )
            except Lunch.DoesNotExist:
                ret.update(status='No lunch')
        else:
            ret.update(status='No lunch')
        return ret

    class Meta:
        model = Profile
        fields = ('id', 'name', 'day')


class ProfileLunch(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'lunch', 'lunch_weekly', 'veggie')


class TeamProfile(serializers.ModelSerializer):
    team_leader_id = serializers.UUIDField(required=False)
    project_manager_id = serializers.UUIDField(required=False)

    class Meta:
        model = Profile
        fields = ('id', 'name', 'phone', 'team_leader_id', 'project_manager_id', 'user')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('image'):
            ret.update(image=settings.MEDIA_IMAGE + ret.get('image'))
        role = "Member"
        if ret.get('user') and ret.get('user') == instance.team_leader_id:
            role = "Leader"
        if ret.get('user') and ret.get('user') == instance.project_manager_id:
            role = "Project manager"
        ret.update(
            title=role,
            email=instance.user.email
        )
        return ret
