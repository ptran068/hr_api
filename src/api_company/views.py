from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from api.authentications import APIAuthentication
from api_base.views import BaseViewSet
from api_company.models import Company
from api_company.serializers import CompanySerizlizer


class CompanyViewSet(BaseViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerizlizer
    pagination_class = None
    authentication_classes = (APIAuthentication,)
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'list': [AllowAny]}

    def create(self, request, *args, **kwargs):
        if Company.objects.exists():
            return Response({'error': 'Company setting was existed!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        company = Company.objects.get_company()
        serializer = self.get_serializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        company = Company.objects.get_company()
        serializer = self.get_serializer(company, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



