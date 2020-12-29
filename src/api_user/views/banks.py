from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api_base.views import BaseViewSet
from api_user.models.banks import Banks
from api_user.serializers.related_profile import BanksSerializer


class BankViewSet(BaseViewSet):
    serializer_class = BanksSerializer
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'destroy': [IsAdminUser]}

    def list(self, request, *args, **kwargs):
        banks = Banks.objects.all()
        banks_serializer = self.get_serializer(banks, many=True)
        return Response(banks_serializer.data)

    def create(self, request):
        bank_serializer = self.get_serializer(data=request.data)
        bank_serializer.is_valid(raise_exception=True)
        bank_serializer.save()
        return Response(bank_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        bank_id = kwargs.get('pk')
        if not bank_id:
            data = {"detail": "bank not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        Banks.objects.filter(id=bank_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
