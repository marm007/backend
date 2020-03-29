from rest_framework import serializers

from api.models import Post, User, UserMeta, Comment
from api.serializers.album import AlbumSerializer
from api.serializers.like import LikeSerializer


class UserMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMeta
        fields = ('photo',)


class UserSerializer(serializers.ModelSerializer):
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'author_name', 'user')


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    album_set = AlbumSerializer(many=True, read_only=True)
    liked = LikeSerializer(many=True, read_only=True)
    comments = PostCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'image', 'description', 'likes', 'album_set', 'liked', 'user', 'comments')


class PostSerializerLike(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    album_set = AlbumSerializer(many=True, read_only=True)
    liked = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'image', 'description', 'likes', 'album_set', 'liked', 'user')
