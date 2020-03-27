from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import Follower
from api.permissions import ContainsOrReadOnly
from api.serializers.follower import FollowerModelSerializer


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