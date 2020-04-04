import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import AllowAny

from api.models import Post, User, Relation

from api.serializers.user import UserFilterSerializer


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username': ['istartswith', ],
        }


class UsersFilterList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserFilterSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = UserFilter


class UserListFollowedPostsFilter(django_filters.FilterSet):
    created = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Post
        fields = {
            'likes': ['exact', 'lt', 'gt'],
            'created': ['exact', ],
        }


class UserListFollowedRelationsFilter(django_filters.FilterSet):
    created = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Relation
        fields = {
            'user__username': ['exact', 'contains'],
            'created': ['exact', ],
        }
