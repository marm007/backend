from copy import Error
import json
from datetime import timedelta

import cloudinary
from django.contrib.auth import authenticate, login, logout as d_logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests
from rest_framework import status, viewsets, generics
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import UserListFollowedPostsFilter, UserListFollowedRelationsFilter
from api.models import User, Follower, Post, Relation
from api.permissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, \
    IsOwnerOrIsAdminOrIsFollowing, IsOwnerOrIsAdminOrIsFollowingForProfile, is_following
from api.serializers.post import PostProfileSerializer, PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserSerializer, UserFollowSerializer, UserRetrieveSerializer
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework.filters import OrderingFilter
from django.dispatch import receiver

from axes.signals import user_locked_out, user_login_failed
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied("Too many failed login attempts")


@api_view(['POST'])
@permission_classes([AllowAny])
def auth(request):
    try:
        user = request.data
        user = authenticate(request=request, email=user.get(
            'email'), password=user.get('password'))

        if user is not None:
            login(request, user)

            refresh = RefreshToken.for_user(user)

            serializer = UserSerializer(user)

            json_data = {'refresh': str(refresh), 'access': str(
                refresh.access_token), 'user': serializer.data, }

            return Response(json_data, status=status.HTTP_200_OK)
        else:
            res = {'detail': 'Bad login or password'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        print(err)
        res = {'detail': 'Something went wrong!'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def logout(request):
    d_logout(request._request)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([BasicAuthentication, ])
def auth_old(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    serializer = UserSerializer(user)
    json_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': serializer.data,
    }
    return Response(json_data, status=status.HTTP_200_OK)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def recaptcha_validate(request):
    body = json.loads(request.body)
    token = body['recaptcha']
    res = {}
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token,
        #'remoteip': get_client_ip(request) #
    }
    if token is None:
        res = {
            'message': 'Token is empty or invalid',
        }
        return Response(res, status=status.HTTP_201_CREATED)
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    res["status"] = verify_rs.get("success", False)
    res['message'] = verify_rs.get('error-codes', None) or "Unspecified error."
    return Response(res)


@api_view(['POST'])
@permission_classes([AllowAny])
def activate_account_link_clicked(request, *args, **kwargs):
    token = request.data.get('activation_token')
    res = {
        'message': 'Account activated',
    }
    user = User.objects.filter(meta__activation_token=token).first()

    if bool(user):
        user.is_active = True
        user.save()
        user.meta.activation_token = ''
        user.meta.activation_token_expires = timezone.now()
        user.meta.save()
        return Response(res, status=status.HTTP_200_OK)
    else:
        res = {
            'message': 'Invalid activation token',

        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


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
            html_content = '<a href="{}/reset/{}/">Click to reset your password</a>'.format(
                settings.FRONT_URL, verify_link)

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
    if instance.meta.avatar:
        cloudinary.uploader.destroy(instance.meta.avatar.public_id)


class UserListPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrIsAdminOrIsFollowing)
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user=user)


class UserListPostsProfile(generics.ListAPIView):
    permission_classes = [AllowAny, IsOwnerOrIsAdminOrIsFollowingForProfile]
    serializer_class = PostProfileSerializer

    def get_queryset(self):
        user = User.objects.filter(id=self.kwargs.get('pk')).first()
        return Post.objects.filter(user=user)

    filter_backends = [OrderingFilter]

    ordering_fields = ['created']

    ordering = ('-created',)


class UserListFollowedPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(Q(user=user) | Q(user__followers__user__id=user.id)).distinct()

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['likes', 'created']

    ordering = ('-created',)

    filterset_class = UserListFollowedPostsFilter


class UserListFollowedRelations(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RelationSerializer

    def get_queryset(self):
        user = self.request.user
        return Relation.timeframed.filter(Q(user=user) | Q(user__followers__user__id=user.id)).distinct()

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['created', ]

    filterset_class = UserListFollowedRelationsFilter


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
            serializer = UserFollowSerializer(
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
            serializer = UserFollowSerializer(
                instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        else:
            Follower.objects.create(
                user=request.user, user_being_followed=instance)
            serializer = UserFollowSerializer(
                instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
