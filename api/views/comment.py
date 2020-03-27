from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import Comment
from api.permissions import IsOwnerOrReadOnly
from api.serializers.comment import CommentSerializer


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

