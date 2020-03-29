from rest_framework import status, viewsets, serializers, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Comment, Post
from api.permissions import IsOwnerOrReadOnly,  IsOwnerOrIsAdminOrIsFollowing
from api.serializers.comment import CommentSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsOwnerOrIsAdminOrIsFollowing]

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        _id = self.kwargs.get('pk')
        try:
            post = Post.objects.get(id=_id)
            if post:
                serializer.save(user=self.request.user, author_name=self.request.user.username, post=post)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Post with id {} dose not exists.'.format(_id))
