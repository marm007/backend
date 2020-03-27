from rest_framework import serializers

from api.models import UserMeta, User
from api.serializers.follower import FollowerSerializer, FollowedSerializer
from api.serializers.like import LikeSerializerUser
from api.serializers.relation import RelationSerializer


class UserMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMeta
        fields = ('photo',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    meta = UserMetaSerializer(required=True)
    liked = LikeSerializerUser(many=True, read_only=True)
    relations = RelationSerializer(many=True, read_only=True)
    followers = FollowerSerializer(many=True, read_only=True)
    followed = FollowedSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password',
                  'meta', 'liked', 'relations', 'followers', 'followed')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        meta_data = validated_data.pop('meta')
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserMeta.objects.create(user=user, **meta_data)
        return user

    def update(self, instance, validated_data):
        meta_data = validated_data.pop('meta')
        meta = instance.meta

        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.email = validated_data.get('email', instance.email)

        meta.photo = meta_data.get('photo', meta.photo)
        meta.save()

        instance.save()

        return instance


class UserRelationSerializer(serializers.HyperlinkedModelSerializer):
    meta = UserMetaSerializer()
    relations = RelationSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'meta', 'relations')
