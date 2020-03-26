from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from api.models import User


class ContainsOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        print('FORM PERMISION')
        print(view)

        print(request.user.id)
        print(obj.follower.id)
        print(obj.followed.id)
        return request.user.id == obj.follower.id or request.user.id == obj.followed.id


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            return obj == request.user


class IsCreationOrIsAuthenticatedOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create' or request.method in SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                return True
            else:
                return False

