from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Lunch
from .serializers import LunchSerializer
from api.middlewares.pagination import CustomPagination
from api_providers.models import Provider
import datetime
from api_user_lunch.models import UserLunch 
from .services import LunchServices
from rest_framework.generics import ListAPIView


class LunchesList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        lunches = Lunch.objects.all()
        serializer = LunchSerializer(lunches, many=True)
        return Response(serializer.data)
 
    def post(self, request):
        serializer = LunchSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                new_lunch = LunchServices.create_many(
                    list_lunches=request.data.get('list_lunches'),
                )
                return Response(dict(msg='You have just created lunch for {} days'.format(len(new_lunch))))
            except Exception as e:
                return Response({'error_msg': str(e)})
            


class HandleLunch(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        provider = request.data.get('provider')

        serializer = LunchSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                LunchServices.create(
                    serializer=serializer,
                    provider=provider
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error_msg': str(e)})

    def get_object(self, pk):
        try:
            lunch = Lunch.objects.get(id=pk)
            return lunch
        except Lunch.DoesNotExist:
            return Response(dict(msg='Lunch not found'))

    def put(self, request, pk):
        lunch_instance = self.get_object(pk)
        serializer = LunchSerializer(instance=lunch_instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                LunchServices.update(
                    serializer=serializer,
                    pk=pk,
                    date=request.data.get('date')
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error_msg': str(e)})

    def delete(self, request, pk):
        lunch = self.get_object(pk)
        lunch.delete()
        return Response(dict(msg=f"lunch with id {pk} has been deleted."), status=status.HTTP_204_NO_CONTENT)
