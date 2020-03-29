from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Follower
from api.serializers.follower import FollowerModelSerializer


class FollowerRetrieve(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        follower = Follower.objects.filter(id=kwargs.get('pk')).first()
        if bool(follower):
            serializer = FollowerModelSerializer(follower)
            return Response(serializer.data)
        else:
            return Response({'error': 'Object dose not exists.'}, status=status.HTTP_404_NOT_FOUND)