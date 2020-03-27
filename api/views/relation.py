from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny


from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models import Relation
from api.permissions import IsOwnerOrReadOnly
from api.serializers.relation import RelationSerializer


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
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
