from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_base.views import BaseViewSet
from api_workday.models import Holiday
from api_workday.serializers import HolidaysSerizlizer


class HolidayViewSet(BaseViewSet):
    queryset = Holiday.objects.all().order_by('date')
    serializer_class = HolidaysSerizlizer
    authentication_classes = (APIAuthentication,)
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'list': [AllowAny]}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not Holiday.objects.filter(date=request.data['date']).exists():
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data)
        return Response({'status': 'Holiday already exists'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        holiday = self.get_object()
        self.perform_destroy(holiday)
        return Response(status=status.HTTP_204_NO_CONTENT)

