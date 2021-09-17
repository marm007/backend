import cloudinary
from api.models import Follower, Post, User
from api.permissions import (IsCreationOrIsAuthenticatedOrReadOnly,
                             IsOwnerOrIsAdminOrIsFollowingForProfile,
                             IsOwnerOrReadOnly)
from api.serializers.post import PostProfileSerializer
from api.serializers.user import (UserProfileSerializer,
                                  UserRetrieveSerializer, UserSerializer)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@receiver(pre_delete, sender=User)
def photo_delete(sender, instance, **kwargs):
    if instance.meta.avatar:
        cloudinary.uploader.destroy(instance.meta.avatar.public_id)


class UserRetrieveProfile(generics.RetrieveAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()


class UserListPostsProfile(generics.ListAPIView):
    permission_classes = [AllowAny, IsOwnerOrIsAdminOrIsFollowingForProfile]
    serializer_class = PostProfileSerializer

    def get_queryset(self):
        user = User.objects.filter(id=self.kwargs.get('pk')).first()
        return Post.objects.filter(user=user)

    filter_backends = [OrderingFilter]

    ordering_fields = ['created']

    ordering = ('-created',)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        try:
            validate_password(request.data.get('password'))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            print(e)
            res = {
                'errors': e
            }
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            serializer = UserProfileSerializer(
                instance, context={'request': request})
            return Response(serializer.data)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated],
            url_path='follow', url_name='user_follow')
    def user_follow(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.followers.filter(
            user=request.user, user_being_followed=instance)
        is_already_followed = bool(queryset)
        if is_already_followed:
            queryset.delete()
            serializer = UserProfileSerializer(
                instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        else:
            Follower.objects.create(
                user=request.user, user_being_followed=instance)
            serializer = UserProfileSerializer(
                instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
