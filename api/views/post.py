from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny


from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models import Post
from api.permissions import IsOwnerOrReadOnly
from api.serializers.like import LikeSerializer
from api.serializers.post import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated],
            url_path='like', url_name='photos_like')
    def like(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.liked.filter(user_id=request.user.id)
        is_already_liked = bool(queryset)
        if is_already_liked:
            queryset.delete()
            data = {'likes': instance.likes - 1}
            serializer = PostSerializer(instance, data=data, partial=True)
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
                serializer = PostSerializer(instance, data=data, partial=True)
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
        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostSerializer(instance)
        return Response(serializer.data)

