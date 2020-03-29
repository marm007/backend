from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Follower
from api.permissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from api.serializers.user import UserSerializer, UserFollowSerializer, UserRetrieveSerializer


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
    if email is not None :
        if bool(User.objects.filter(email=email).first()):
            token = get_random_string(length=32)
            verify_link = token
            subject = 'Reset your password'
            from_email = 'appfoto375@gmail.com'
            to = email
            send_mail(subject, 'http://127.0.0.1:8000/api/password/reset/' + verify_link + '/', from_email, [to])
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
def validate_email_token(request, *args, **kwargs):
    token = kwargs.get('token')
    res = {
        'message': 'Password reset successfully',
    }
    user = User.objects.filter(meta__reset_password_token=token,
                               meta__reset_password_expires__gte=timezone.now()).first()

    if bool(user):
        try:
            user.set_password(request.data.get('password'))
            user.save()
            user.meta.reset_password_token = ''
            user.meta.reset_password_expires = timezone.now()
            user.meta.save()
            return Response(res, status=status.HTTP_200_OK)
        except IntegrityError as error:
            return Response({'error': error.__str__()}, status=status.HTTP_400_BAD_REQUEST)

    else:
        res = {
            'message': 'Invalid reset token',

        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id is not None:
            if instance.id is request.user.id:
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                serializer = UserRetrieveSerializer(instance)
                return Response(serializer.data)
        else:
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated],
            url_path='follow', url_name='user_follow')
    def user_follow(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.followers.filter(user_being_followed=instance)
        is_already_followed = bool(queryset)
        if is_already_followed:
            queryset.delete()
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        else:
            Follower.objects.create(user=request.user, user_being_followed=instance)
            serializer = UserFollowSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
