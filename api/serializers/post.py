from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework import serializers

from api.models import Post, PostImageMeta, User, UserMeta, Comment


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


class CommentProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', )


class CommentPostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)
    body = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        # list_serializer_class = FilteredCommentsSerializer
        fields = ('id', 'body', 'author_name', 'user')


class PostImageMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    post = PrimaryKeyRelatedField

    class Meta:
        model = PostImageMeta
        fields = '__all__'

    def create(self, validated_data):
        return PostImageMeta.objects.create(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    comments = CommentPostSerializer(
        many=True, read_only=True, source="output_comments")
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'image', 'description', 'likes',
                  'user', 'comments', 'created', 'is_liked', 'image_metadata')

    def create(self, validated_data):
        post = Post(**validated_data)
        post.save()
        image_metadata = post.image_metadata()
        image_metadata['post'] = post.id
        serializer = PostImageMetaSerializer(data=image_metadata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return post

    def get_is_liked(self, instance):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            queryset = instance.liked.filter(user=request.user)
            return bool(queryset)
        else:
            return False


class PostProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'image', 'likes', 'comments')

    def get_comments(self, instance):
        comments = CommentProfileSerializer(
            instance=instance.comments, many=True)
        return len(comments.data)
