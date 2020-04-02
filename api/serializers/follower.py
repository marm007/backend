from rest_framework import serializers

from api.models import Follower


class FollowerModelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = serializers.PrimaryKeyRelatedField
    user_being_followed = serializers.PrimaryKeyRelatedField

    class Meta:
        model = Follower
        fields = ('id', 'user', 'user_being_followed')

