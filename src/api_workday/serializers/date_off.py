from rest_framework import serializers

from api_workday.models.date_off import DateOff


class DateOffSerizlizer(serializers.ModelSerializer):
    request_off = serializers.SerializerMethodField("get_request")

    def get_request(self, obj):
        return {'id': obj.request_off.id,
                'type_type': obj.request_off.type_off.type,
                'type_title': obj.request_off.type_off.title,
                'type_is_ot_days': obj.request_off.type_off.is_ot_days,
                'type_is_paid_salary': obj.request_off.type_off.is_paid_salary,
                'type_add_sub_day_off': obj.request_off.type_off.add_sub_day_off,
                }

    class Meta:
        model = DateOff
        fields = ['id', 'request_off', 'date', 'type', 'lunch']
