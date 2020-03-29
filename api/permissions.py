from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


def is_following(_list, _filter):
    for x in _list:
        if _filter(x):
            return True
    return False


class IsFollowingOrIsFollowed(permissions.BasePermission):
    """
    Custom permission to only allow followers to remove following or followed to remove follower.
    """

    def has_object_permission(self, request, view, obj):
        print(obj)

        return request.user.id == obj.user.id or request.user.id == obj.user_being_followed.id


class IsOwnerOrIsAdminOrIsFollowing(permissions.BasePermission):
    """
    Custom permission to allow followers, admins to show posts, comments and relations of authors and owners to edit it.
    """
    message = 'Watching posts is not allowed for not followers.'

    def has_object_permission(self, request, view, obj):
        is_owner = request.user.id == obj.user.id
        print(is_owner)
        if is_owner:
            return True
        else:
            if request.user.is_staff:
                return True
            is_follower = is_following(request.user.followed.all(),
                                       lambda x: x.user_being_followed.id == obj.user.id)
            print(is_follower)
            return is_follower


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
