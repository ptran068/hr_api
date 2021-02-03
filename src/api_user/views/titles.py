from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api_base.views import BaseViewSet
from api_user.models.titles import Titles
from api_user.serializers.user import TitlesSerializer


class TitleViewSet(BaseViewSet):
    serializer_class = TitlesSerializer
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'destroy': [IsAdminUser]}

    def list(self, request, *args, **kwargs):
        titles = Titles.objects.all()
        titles_serializer = self.get_serializer(titles, many=True)
        return Response(titles_serializer.data)

    def create(self, request):
        title_serializer = self.get_serializer(data=request.data)
        title_serializer.is_valid(raise_exception=True)
        title_serializer.save()
        return Response(title_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        title_id = kwargs.get('pk')
        if not title_id:
            data = {"detail": "title not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        Titles.objects.filter(id=title_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
