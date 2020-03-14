from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.models import Album
from api.premissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from .serializers import *

from rest_framework import status, viewsets
from rest_framework.response import Response
from django.core import serializers as s

class UsersViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def partial_update(self, request, *args, **kwargs):
        # update likes here
        return Response({}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id}
        image = request.data.get('image')
        description = request.data.get('description')
        data.update({'image': image, 'description': description})
        serializer = PhotoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Album):
            return str(obj)
        return super().default(obj)


class AlbumViewSet(viewsets.ModelViewSet):

    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id,
                'name': request.data.get('name', '')}
        serializer = AlbumSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        album = self.get_object()
        serializer = AlbumSerializer(album, data=request.data, partial=True)
        # album.photos.add(request.data.get('photos', ''))
        # album.save()
        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
