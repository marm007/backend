from api.filters import (UserListFollowedPostsFilter,
                         UserListFollowedRelationsFilter)
from api.models import Post, Relation
from api.serializers.dashboard import DashboardSerializer
from api.serializers.post import PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserRetrieveSerializer
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class UserMeRetrieve(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = UserRetrieveSerializer

    def get_queryset(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = DashboardSerializer(instance=request.user)
    return Response(user.data, status=status.HTTP_200_OK)


class UserMeListFollowedPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(Q(user=user) | Q(user__followers__user__id=user.id)).distinct()

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['likes', 'created']

    ordering = ('-created',)

    filterset_class = UserListFollowedPostsFilter


class UserMeListFollowedRelations(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RelationSerializer

    def get_queryset(self):
        user = self.request.user
        return Relation.timeframed.filter(Q(user=user) | Q(user__followers__user__id=user.id)).distinct()

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ('created', )

    filterset_class = UserListFollowedRelationsFilter
