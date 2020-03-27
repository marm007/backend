from datetime import timedelta

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

from api.models import Relation
from api.premissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, ContainsOrReadOnly
from .serializers import *

from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        data = request.data
        data.update({'profile': {'photo': request.data.get('profile_photo')}})
        serializer = self.get_serializer(data=data)
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
        serializer = UserPostsSerializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserMyProfileSerializer(instance)
        return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated],
            url_path='like', url_name='photos_like')
    def like(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.liked.filter(user_id=request.user.id)
        is_already_liked = bool(queryset)
        if is_already_liked:
            queryset.delete()
            data = {'likes': instance.likes - 1}
            serializer = PhotoUserSerializer(instance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            photo_id = instance.id
            user_id = request.user.id
            data = {'photo_id': photo_id, 'user_id': user_id}
            like_serializer = LikeSerializer(data=data)

            if like_serializer.is_valid():
                like_serializer.save()
                data = {'likes': instance.likes + 1}
                serializer = PhotoUserSerializer(instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    json_data = serializer.data
                    return Response(json_data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id}
        image = request.data.get('image')
        description = request.data.get('description')
        data.update({'image': image, 'description': description})
        serializer = PhotoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = PhotoUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PhotoUserSerializer(instance)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id, 'photo_id': kwargs.get('pk'),
                'body': request.data.get('body', ''),
                'author_name': request.user.username}
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        photo_id = kwargs.get('pk')
        queryset = Comment.objects.filter(photo=photo_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(methods=['put'], detail=True,
            url_path='photos/delete', url_name='photos_delete')
    def delete_photos(self, request, *args, **kwargs):
        album = self.get_object()
        photos_to_delete = request.data.get('photos')
        album.photos.remove(*photos_to_delete)
        serializer = self.get_serializer(album)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id,
                'name': request.data.get('name', '')}
        serializer = AlbumSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        album = self.get_object()
        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializerGet
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id,
                'user': request.user}
        image = request.data.get('image')
        data.update({'image': image})
        serializer = RelationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ContainsOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'follower': request.user.id, 'followed': request.data.get('followed')}
        serializer = FollowerModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)