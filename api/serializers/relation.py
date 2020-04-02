from rest_framework import serializers

from api.models import Relation, UserMeta, User


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField

    class Meta:
        model = UserMeta
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class RelationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)

    class Meta:
        model = Relation
        fields = ('id', 'image', 'created', 'user')
