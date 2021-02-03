from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return request.user.is_staff or obj == request.user
        return request.user.is_staff or obj.user == request.user