from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from api.authentications import APIAuthentication
from api_user.models.profile import Profile
from api_workday.services.remain_leave import RemainLeaveService
from rest_framework.response import Response


class AddBonusView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [APIAuthentication]

    def post(self, request, format=None):
        profile = Profile.objects.get_profile_by_id(id=request.data.get('profile_id'))
        try:
            bonus = float(request.data.get("bonus"))
            return Response(RemainLeaveService.add_bonus(profile, bonus).data)
        except:
            return Response({'status': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


