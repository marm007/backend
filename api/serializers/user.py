from django.core.mail import EmailMultiAlternatives
from rest_framework import serializers
from django.utils import timezone

from api.models import UserMeta, User, Like
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import timedelta


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    avatar = serializers.FileField(required=False)

    class Meta:
        model = UserMeta
        fields = ('avatar', 'is_private')


class UserFilterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class LikeSerializerUser(serializers.ModelSerializer):
    id = serializers.UUIDField

    class Meta:
        model = Like
        fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer(required=False)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    relations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followed = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password',
                  'meta', 'likes', 'relations', 'followers', 'followed', 'posts', 'comments')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if validated_data.get('meta'):
            meta_data = validated_data.pop('meta')
        else:
            meta_data = {}
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.is_active = False
        user.set_password(password)

        token = get_random_string(length=32)
        verify_link = token

        subject = 'Activate your account'
        from_email = 'appfoto375@gmail.com'
        to = user.email
        html_content = '<a href="{}/activate/{}/">Click to activate your account</a>'.format(settings.FRONT_URL, verify_link)

        msg = EmailMultiAlternatives(subject, '', from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        meta_data["activation_token"] = token
        date_end = timezone.now() + timezone.timedelta(hours=5)
        meta_data["activation_token_expires"] = date_end
        user.save()
        UserMeta.objects.create(user=user, **meta_data)
        return user

    def update(self, instance, validated_data):
        meta_exists = validated_data.get('meta')
        if meta_exists:
            meta_data = validated_data.pop('meta')
        meta = instance.meta

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))

        if validated_data.get('username'):
            instance.username = validated_data.get('username')

        if validated_data.get('email'):
            instance.email = validated_data.get('email')

        if meta_exists:
            if meta_data.get('avatar'):
                meta.avatar = meta_data.get('avatar', meta.avatar)
            if meta_data.get('is_private', None) is not None:
                meta.is_private = meta_data.get('is_private')
                meta.save()

        instance.save()

        return instance


class UserFollowSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followed = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'meta', 'followers', 'followed', 'posts')


class UserRetrieveSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    relations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'meta', 'posts', 'relations')
