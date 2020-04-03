import django_filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.models import Post, Comment, User, Relation

from api.serializers.post import PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserFilterSerializer
from rest_framework.filters import OrderingFilter


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username': ['icontains', ],
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


class UserListFollowedPostsFilterList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(Q(user__followers__user__id=user.id))

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['likes', 'created']

    ordering = ('-created',)

    filterset_class = UserListFollowedPostsFilter


class UserListFollowedRelationsFilterList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RelationSerializer

    def get_queryset(self):
        user = self.request.user
        return Relation.timeframed.filter(Q(user__followers__user__id=user.id) |
                                          Q(user=user))

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['created', ]

    filterset_class = UserListFollowedRelationsFilter

