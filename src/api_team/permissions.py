from rest_framework import permissions

from api_base.services import Utils
from api_team.models import Team
from api_user.models import Profile


class IsProjectManager(permissions.BasePermission):
    """
    Allows access only to project managers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_project_manager)

