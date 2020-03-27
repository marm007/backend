from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models import Album
from api.permissions import IsOwnerOrReadOnly
from api.serializers.album import AlbumSerializer


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

