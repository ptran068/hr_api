from rest_framework.response import Response
from api_user.models import Profile
from api_base.views.base import BaseViewSet
from api_workday.services.calendar import CalendarServices


class CalendarViewSet(BaseViewSet):

    def list(self, request, *args, **kwargs):
        response = []
        for profile in Profile.objects.all():
            response.extend(CalendarServices.get_lay_days_by_profile(profile))
        return Response(response)

    def retrieve(self, request, *args, **kwargs):
        profile = request.user.profile
        return Response(CalendarServices.get_lay_days_by_profile(profile))
