from rest_framework import serializers
from api_user.models import Profile
from .models import Event



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        event = Event.objects.filter(profile_id=ret.get('id')).first()
        if event:
            ret.update(event=event.id)
        return ret


class EventSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    
    class Meta:
        model = Event
        fields = '__all__'

