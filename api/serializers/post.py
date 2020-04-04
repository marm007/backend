from rest_framework import serializers

from api.models import Post, User, UserMeta, Comment
from api.serializers.like import LikeSerializer


class FilteredCommentsSerializer(serializers.ListSerializer):
    """Serializer to filter the active system, which is a boolen field in
       System Model. The value argument to to_representation() method is
      the model instance"""

    def update(self, instance, validated_data):
        pass

    def to_representation(self, data):
        data = data.filter(active=True)
        return super(FilteredCommentsSerializer, self).to_representation(data)


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


class CommentPostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)
    body = serializers.StringRelatedField(read_only=True)
    active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment
        list_serializer_class = FilteredCommentsSerializer
        fields = ('id', 'body', 'author_name', 'user', 'active')


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    liked = LikeSerializer(many=True, read_only=True)
    comments = CommentPostSerializer(many=True, read_only=True)

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
