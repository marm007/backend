from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.premissions import IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
from .serializers import *

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


class AddPhoto(APIView):
    # parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = {'user_id': request.user.id}
        image = request.data.get('image')
        data.update({'image': image})
        serializer = PhotoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddPhotoViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = {'user_id': request.user.id}
        image = request.data.get('image')
        data.update({'image': image})
        serializer = PhotoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCreationOrIsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


