from rest_framework import serializers

from api.models import Post, User, UserMeta, Comment
from api.serializers.like import LikeSerializer


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    avatar = serializers.FileField()

    class Meta:
        model = UserMeta
        fields = ('avatar', )


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class PostCommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'author_name', 'user')


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    liked = LikeSerializer(many=True, read_only=True)
    comments = PostCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'image',
                  'description', 'likes', 'liked', 'user', 'comments', 'created')


class PostSerializerLike(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    liked = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'image', 'description', 'likes', 'liked', 'user')
