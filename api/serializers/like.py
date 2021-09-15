from rest_framework import serializers

from api.models import Like, UserMeta, User, Post


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField

    class Meta:
        model = UserMeta
        fields = ('avatar', )


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField

    class Meta:
        model = Post
        fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField

    class Meta:
        model = User
        fields = ('id',)


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ('user', )



