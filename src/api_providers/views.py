from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Provider
from .serializers import ProviderSerializer
from api.middlewares.pagination import CustomPagination


class HandleProvider(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        providers = Provider.objects.all()
        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProviderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def get_object(self, pk):
        provider = Provider.objects.filter(id=pk).first()
        if provider is None:
            return Response(dict(msg= 'provider not found'))
        return provider

    def put(self, request, pk):
        serializer = ProviderSerializer(instance=self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        provider = self.get_object(pk)
        provider.delete()
        return Response({
            "msg": "Provider with id `{}` has been deleted.".format(pk)},
            status=status.HTTP_204_NO_CONTENT
        )
