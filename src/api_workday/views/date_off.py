from api_workday.serializers.date_off import DateOffSerizlizer
from api_workday.models.date_off import DateOff
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class DateOffView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, format=None):
        date_off = DateOff.objects.all()
        serializer = DateOffSerizlizer(date_off, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = DateOffSerizlizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
