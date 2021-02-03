from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_user.models import Profile
from api_workday.services.statistic import StatisticServices


class StatisticUserView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIAuthentication]

    def get(self, request):
        profile = Profile.objects.get(id=request.user.profile.id)
        year = request.query_params.get('y')
        data = StatisticServices.get_date_off_for_statistic_user(year, profile)
        return Response(data, status=status.HTTP_200_OK)
