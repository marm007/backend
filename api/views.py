from .serializers import *

from rest_framework import status, permissions
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
        return Response(data={"hello":"world"}, status=status.HTTP_200_OK)


class AddPhoto(APIView):

    def post(self, request):
        print(request.user)
        serializer = PhotoSerializer(data=request.data)
        print(serializer.fields)
        if serializer.is_valid():
            photo = serializer.save()
            if photo:
                json = request.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
