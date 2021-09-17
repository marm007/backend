from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework import serializers

from api.models import Post, PostMeta, User, UserMeta, Comment


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserMeta
        fields = ('avatar', )

    def get_avatar(self, instance):
        if instance.avatar:
            instance.avatar.url_options.update({'secure': True})
            return instance.avatar.url
        else:
            return 'https://res.cloudinary.com/marm007/image/upload/v1585912225/avatar_iahjs2.png'


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
        fields = ('id', 'body', 'author_name', 'user')


class PostMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    post = PrimaryKeyRelatedField

    class Meta:
        model = PostMeta
        fields = '__all__'

    def create(self, validated_data):
        return PostMeta.objects.create(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    comments = CommentPostSerializer(
        many=True, read_only=True, source="output_comments")
    is_liked = serializers.SerializerMethodField()
    image_meta = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'description', 'image', 'likes',
                  'user', 'comments', 'created', 'is_liked', 'image_meta')
        extra_kwargs = {
            'image': {'write_only': True}
        }

    def create(self, validated_data):
        post = Post(**validated_data)
        post.save()
        image_metadata = post.image_metadata()
        image_metadata['post'] = post.id
        serializer = PostMetaSerializer(data=image_metadata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return post

    def get_image_meta(self, instance):
        meta = {}
        try:
            meta['width'] = instance.meta.width
            meta['height'] = instance.meta.height
            instance.image.url_options.update({'secure': True})
            meta['url'] = instance.image.url
        except Exception as e:
            print(e)
        return meta

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
    image_meta = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'likes', 'comments', 'image_meta')

    def get_comments(self, instance):
        comments = CommentProfileSerializer(
            instance=instance.comments, many=True)
        return len(comments.data)

    def get_image_meta(self, instance):
        meta = {}
        try:
            meta['width'] = instance.meta.width
            meta['height'] = instance.meta.height
            instance.image.url_options.update({'secure': True})
            meta['url'] = instance.image.url
        except Exception as e:
            print(e)
        return meta
