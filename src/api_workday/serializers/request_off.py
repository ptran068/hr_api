from rest_framework import serializers

from api_workday.models.request_off import RequestOff
from api_workday.serializers.date_off import DateOffSerizlizer


class RequestOffSerializer(serializers.ModelSerializer):
    date_off = DateOffSerizlizer(many=True, read_only=True)
    type_off = serializers.SerializerMethodField("get_type")
    profile = serializers.SerializerMethodField("get_profile")
    request_detail = serializers.SlugRelatedField(many=True, slug_field='comment', read_only=True)

    def get_type(self, obj):
        return {'id': obj.type_off.id,
                'type': obj.type_off.type,
                'title': obj.type_off.title,
                'add_sub_day_off': obj.type_off.add_sub_day_off,
                'is_ot_days': obj.type_off.is_ot_days,
                'is_paid_salary': obj.type_off.is_paid_salary
                }

    def get_profile(self, obj):
        return {'id': obj.profile.id,
                'name': obj.profile.name
                }

    class Meta:
        model = RequestOff
        fields = '__all__'
        read_only_fields = ['type_off', 'profile']
