from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from api.authentications import APIAuthentication
from api_user.models import Profile
from api_workday.services.statistic import StatisticServices


class StatisticAdminView(ListAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [APIAuthentication]

    def get(self, request):
        name = request.query_params.get('n')
        email = request.query_params.get('e')
        month = request.query_params.get('m')
        year = request.query_params.get('y')
        profile = Profile.objects.all()
        data = StatisticServices.get_date_off_for_statistic_admin(name, email, month, year, profile)
        page = self.paginate_queryset(data)
        return self.get_paginated_response(page)
