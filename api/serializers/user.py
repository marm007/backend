from rest_framework import serializers

from api.models import UserMeta, User, Like


class UserMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMeta
        fields = ('photo', 'is_private')


class UserFilterSerializer(serializers.ModelSerializer):
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class LikeSerializerUser(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ('id',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    meta = UserMetaSerializer()
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


class UserFollowSerializer(serializers.ModelSerializer):
    meta = UserMetaSerializer()
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followed = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'meta', 'followers', 'followed', 'posts')


class UserRetrieveSerializer(serializers.ModelSerializer):
    meta = UserMetaSerializer()
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    relations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'meta', 'posts', 'relations')
