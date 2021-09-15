import cloudinary
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response

from api.models import Post, Like
from api.permissions import IsOwnerOrReadOnly, IsOwnerOrIsAdminOrIsFollowing
from api.serializers.post import PostSerializer, CommentPostSerializer


@receiver(pre_delete, sender=Post)
def photo_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.image.public_id)


class PostViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [IsAuthenticated,
                          IsOwnerOrReadOnly, IsOwnerOrIsAdminOrIsFollowing]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated],
            url_path='like', url_name='post_like')
    def post_like(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.liked.filter(user=request.user)
        is_already_liked = bool(queryset)
        if is_already_liked:
            queryset.delete()
            serializer = self.get_serializer(
                instance, data={'likes': instance.liked.count()}, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            Like.objects.create(post=instance, user=request.user)
            serializer = self.get_serializer(
                instance, data={'likes': instance.liked.count()}, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=True,
            permission_classes=[IsAuthenticated,
                                IsOwnerOrIsAdminOrIsFollowing],
            url_path="comments_in_post", url_name="comments_in_post")
    def comments_in_post(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.comments.filter(active=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentPostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommentPostSerializer(queryset, many=True)
        return Response(serializer.data)
