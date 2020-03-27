from datetime import timedelta

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny


from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Relation
from api.permissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from api.serializers.post import PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserSerializer, UserMetaSerializer, UserRelationSerializer


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
        token = get_random_string(length=32)
        verify_link = token
        subject = 'Verify Your Email'
        from_email = 'appfoto375@gmail.com'
        to = email
        send_mail(subject, verify_link, from_email, [to])
        user = get_object_or_404(User, email=email)
        user.profile.reset_password_token = token
        user.profile.reset_password_expires = timezone.now() + timedelta(hours=5)
        user.profile.save()
        res = {
            'message': 'Token sent to an email',
        }
        return Response(res, status=status.HTTP_200_OK)
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
        'status': 'success',
        'message': 'Valid',
    }
    print(timezone.now())
    user = User.objects.filter(profile__reset_password_token=token,
                               profile__reset_password_expires__gte=timezone.now()).first()

    if bool(user):
        user.profile.reset_password_token = ''
        user.profile.reset_password_expires = timezone.now()
        user.profile.save()
        return Response(res, status=status.HTTP_200_OK)

    else:
        res = {
            'status': 'failed',
            'message': 'Invalid',
        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        # data = {
        #     'meta': {'photo': request.data.get('meta_photo')},
        #     'password': request.data.get('password'),
        #     'username': request.data.get('username'),
        #     'email': request.data.get('email'),
        # }
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_relations(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserRelationSerializer(instance)
        return Response(serializer.data)

    def get_posts(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostSerializer(instance)
        return Response(serializer.data)



