import cloudinary
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from api.models import Relation
from api.permissions import IsOwnerOrReadOnly, IsOwnerOrIsAdminOrIsFollowing
from api.serializers.relation import RelationSerializer
from datetime import datetime, timedelta


@receiver(pre_delete, sender=Relation)
def photo_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.image.public_id)


class RelationViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Relation.timeframed.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsOwnerOrIsAdminOrIsFollowing]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, start=datetime.now(),
                        end=datetime.now() + timedelta(hours=8))

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
