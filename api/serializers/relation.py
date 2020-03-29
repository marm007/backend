from rest_framework import serializers

from api.models import Relation, UserMeta, User


class UserMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMeta
        fields = ('photo',)


class UserSerializer(serializers.ModelSerializer):
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class RelationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Relation
        fields = ('id', 'image', 'created', 'user')
