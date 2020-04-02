from rest_framework import serializers

from api.models import Comment, User, Post


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    class Meta:
        model = Post
        fields = ('id', )


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    class Meta:
        model = User
        fields = ('id', )


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'author_name', 'user', 'post')

