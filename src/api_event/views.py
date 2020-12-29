from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Event
from .serializers import EventSerializer, ProfileSerializer
from .services import EventServices
from rest_framework.permissions import AllowAny


class SlackEvents(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            EventServices.reminder_admin_set_birthday_slack()
            return Response(dict(msg='Created successfully'))
        except Exception as e:
            return Response({'error_msg': str(e)})


class EventsList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = Event.objects.all()
        serializers = EventSerializer(queryset, many=True)
        return Response(serializers.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                EventServices.create(
                    serializer=serializer,
                    data=request.data
                )
                return Response(dict(msg='Created successfully'))
            except Exception as e:
                return Response({'msg': str(e)})

    def put(self, request, pk):
        serializer = EventSerializer(instance=self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'msg': str(e)})

    def delete(self, request, pk):
        event = Event.objects.filter(id=pk)
        if event:
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(dict(msg='event not found'))

    def get_object(self, pk):
        event = Event.objects.filter(profile_id=pk).first()
        if event is None:
            return Response(dict(msg='event not found'))
        return event


class EventUsersList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            month = request.query_params.get('month')
            user_events = EventServices.get_birthdays_in_month(month)
            serializers = ProfileSerializer(user_events, many=True)
            return Response(serializers.data)
        except Exception as e:
            return Response({'msg': str(e)})
