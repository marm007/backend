from datetime import timedelta

import cloudinary
from django.core.mail import send_mail
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status, viewsets, generics
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Follower, Post
from api.permissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, \
    IsOwnerOrIsAdminOrIsFollowing, IsOwnerOrIsAdminOrIsFollowingForProfile
from api.serializers.post import PostSerializer
from api.serializers.user import UserSerializer, UserFollowSerializer, UserRetrieveSerializer
from backend.settings import FRONT_URL
from django.core.mail import EmailMultiAlternatives

@api_view(['POST'])
@authentication_classes([BasicAuthentication, ])
def auth(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    serializer = UserSerializer(user)
    json_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': serializer.data,
    }
    return Response(json_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    if email is not None:
        if bool(User.objects.filter(email=email).first()):
            token = get_random_string(length=32)
            verify_link = token

            subject = 'Reset your password'
            from_email = 'appfoto375@gmail.com'
            to = email
            html_content = '<a href="{}/reset/{}/">Click to reset your password</a>'.format(FRONT_URL, verify_link)

            msg = EmailMultiAlternatives(subject, '', from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            user = get_object_or_404(User, email=email)
            user.meta.reset_password_token = token
            user.meta.reset_password_expires = timezone.now() + timedelta(hours=5)
            user.meta.save()
            res = {
                'message': 'Token sent to an email',
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'message': 'User with such an email dose nto exists.',
            }
            return Response(res, status=status.HTTP_404_NOT_FOUND)

    else:
        res = {
            'message': 'Non email provided',
        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, *args, **kwargs):
    token = kwargs.get('token')
    res = {
        'message': 'Password reset successfully',
    }
    user = User.objects.filter(meta__reset_password_token=token,
                               meta__reset_password_expires__gte=timezone.now()).first()

    if bool(user):
        password = request.data.get('password')
        if password is not None:
            user.set_password(request.data.get('password'))
            user.save()
            user.meta.reset_password_token = ''
            user.meta.reset_password_expires = timezone.now()
            user.meta.save()
            return Response(res, status=status.HTTP_200_OK)
        return Response({'error': {'Password cannot be none'}}, status=status.HTTP_400_BAD_REQUEST)

    else:
        res = {
            'message': 'Invalid reset token',

        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@receiver(pre_delete, sender=User)
def photo_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.meta.avatar.public_id)


class UserListPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrIsAdminOrIsFollowing)
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user=user)


class UserListFollowedPosts(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdminOrIsFollowingForProfile]
    serializer_class = PostSerializer

    def get_queryset(self):
        user = User.objects.filter(id=self.kwargs.get('pk')).first()
        return Post.objects.filter(user=user)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        print(instance.id)
        if request.user.id is not None:
            print('afsafafs')
            print(request.user.id)

            if instance.id == request.user.id:
                print('zcxxxz')

                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                serializer = UserRetrieveSerializer(instance)
                return Response(serializer.data)
        else:
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data)

    # @action(methods=['get'], detail=True, permission_classes=[AllowAny],
    #         url_path='followers', url_name='get_followers_posts')
    # def get_followers_posts(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(instance)
    #     posts = Post.objects.fiiter(user__followers__follower__id=instance.id)
    #
    #     print(posts)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated],
            url_path='follow', url_name='user_follow')
    def user_follow(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.followers.filter(user=request.user, user_being_followed=instance)
        is_already_followed = bool(queryset)
        if is_already_followed:
            queryset.delete()
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        else:
            Follower.objects.create(user=request.user, user_being_followed=instance)
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
