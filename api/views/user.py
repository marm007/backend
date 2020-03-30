from datetime import timedelta

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Follower, Post, Relation
from api.permissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from api.serializers.post import PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserSerializer, UserFollowSerializer, UserRetrieveSerializer
from django.db.models import Q


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
            send_mail(subject, 'localhost:4200/reset/' + verify_link + '/', from_email, [to])
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


class ListFollowedPosts(mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        start = int(request.query_params.get('start', 0))
        limit = int(request.query_params.get('limit', 5))
        queryset = Post.objects.filter(Q(user__followers__user__id=request.user.id) |
                                       Q(user=request.user))[start:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListFollowedRelations(mixins.ListModelMixin,
                            GenericViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        start = int(request.query_params.get('start', 0))
        limit = int(request.query_params.get('limit', 10))
        queryset = Relation.objects.filter(Q(user__followers__user__id=request.user.id)
                                           | Q(user=request.user))[start:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
