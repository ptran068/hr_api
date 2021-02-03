from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentications import APIAuthentication
from api_workday.models.request_off import RequestOff
from api_workday.models.type_off import TypeOff
from api_workday.serializers.date_off import DateOffSerizlizer
from api_workday.serializers.request_off import RequestOffSerializer
from api_workday.services.action_request import ActionRequestService, FilterRequestServices
from api_workday.services.request_off import RequestOffServices
from api_workday.services.send_mail import SendMailRequestOff
from api_workday.services.request_off import RequestOffServices
from api_workday.models.date_off import DateOff


class RequestOffDetail(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIAuthentication]

    def post(self, request, format=None):
        data = request.data
        profile = request.user.profile
        type_off_id = request.data.get('type_id')
        type_off = TypeOff.objects.filter(id=type_off_id).first()
        try:
            if RequestOffServices.check_out_of_join_date(data, profile.id):
                return Response({'error': 'There was a request for out of join date'},
                                status=status.HTTP_400_BAD_REQUEST)
            if RequestOffServices.check_available_date_off(profile.id, type_off, data):
                return Response({'error': 'There was a request for over available day!'}, status=status.HTTP_400_BAD_REQUEST)
            if RequestOffServices.check_overlap_date(data, profile.id):
                return Response({'error': 'There was a request for this date!'}, status=status.HTTP_400_BAD_REQUEST)
            request_data = {"reason": data["reason"]}
            requestSerializer = RequestOffSerializer(data=request_data)
            with transaction.atomic():
                if requestSerializer.is_valid():
                    request_off = requestSerializer.save(type_off=type_off, profile=profile)
                request_id = requestSerializer.data['id']
                for date in data["date"]:
                    date_data = {
                        "date": date["date"],
                        "type": date["type"],
                        "lunch": date["lunch"],
                        "request_off": request_id
                    }
                    dateSerializer = DateOffSerizlizer(data=date_data)
                    if dateSerializer.is_valid():
                        dateSerializer.save(request_off=request_off)
                ActionRequestService.create_action_user(request_off, profile.line_manager)
                SendMailRequestOff.send_request(type_off=type_off, name_admin=profile.line_manager.name,
                                                name_user=request_off.profile.name,
                                                list_email=[profile.line_manager.user.email],
                                                date_off=request_off.date_off.all())
            return Response(requestSerializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({'Error': 'Error'}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return RequestOff.objects.get(pk=pk)
        except RequestOff.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        request_off = self.get_object(pk)
        serializer = RequestOffSerializer(request_off)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        request_off = self.get_object(pk)
        serializer = RequestOffSerializer(request_off, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        request_off = self.get_object(pk)
        request_off.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetMyRequest(ListAPIView):
    queryset = RequestOff.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIAuthentication]
    pagination_class = None
    serializer_class = RequestOffSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        request_off = self.queryset.filter(profile=profile).order_by('-created_at')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')
        status_request = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        request_off = FilterRequestServices.filter_multipart(request_off, year, month, day, status_request, search)
        return request_off


class GetAllRequest(ListAPIView):
    queryset = RequestOff.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [APIAuthentication]
    serializer_class = RequestOffSerializer

    def get_queryset(self):
        request_off = self.queryset.all().order_by('-created_at')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')
        status_request = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        request_off = FilterRequestServices.filter_multipart(request_off, year, month, day, status_request, search)
        return request_off
