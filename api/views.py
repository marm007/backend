from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import *

from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = request.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelloWorldView(APIView):

    def get(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)


class AddPhoto(APIView):
    # parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        print(request.user.id)
        print(request.data)

        data = {'user_id': request.user.id}

        name = request.data.get('name')
        image = request.data.get('image')

        print(name)

        data.update({'image': image})
        if name is not None:
            data.update({'name': name})

        serializer = PhotoSerializer(data=data)

        print(data)
        print(serializer.fields)

        if serializer.is_valid():
            serializer.save()
            json = serializer.data
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
