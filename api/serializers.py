from rest_framework import serializers
from api.models import User, UserProfile, Photo, Comment, Like, Album, Relation, Follower


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('photo',)


class LikeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    photo_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('id', 'photo_id', 'user_id')


class LikeSerializerUser(serializers.ModelSerializer):
    photo_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('id', 'photo_id')


class LikeSerializerPhoto(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('id', 'user_id')


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', )


class UserRelationHelperSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')


class RelationSerializer(serializers.ModelSerializer):
    user = UserRelationHelperSerializer(read_only=True)
    user_id = serializers.IntegerField()

    class Meta:
        model = Relation
        fields = ('id', 'image', 'user', 'user_id', 'created')


class FollowerModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follower
        fields = ('id', 'follower', 'followed')


class FollowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follower
        fields = ('id', 'follower')


class FollowedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id',)


class FollowedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follower
        fields = ('id', 'followed')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()
    liked = LikeSerializerUser(many=True, required=False)
    relations = RelationSerializer(many=True, required=False)
    followers = FollowerSerializer(many=True, required=False)
    followed = FollowedSerializer(many=True, required=False)
    # followed = FollowerSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password',
                  'profile', 'liked', 'relations', 'followers', 'followed')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.photo = profile_data.get('photo', profile.photo)
        profile.save()

        return instance


class UserPhotoSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')


class CommentPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('body', 'author_name')

    def create(self, validated_data):
        comment = Comment(**validated_data)
        comment.save()
        return comment


class PostSerializer(serializers.ModelSerializer):
    liked = LikeSerializerPhoto(many=True, required=False)
    comments = CommentPhotoSerializer(many=True, required=False)

    class Meta:
        model = Photo
        fields = ('id', 'image', 'description', 'likes', 'liked', 'comments', 'created')


class UserMyProfileSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()
    liked = LikeSerializerUser(many=True, required=False)
    relations = RelationSerializer(many=True, required=False)
    posts = PostSerializer(source='photos', many=True, required=False)
    followers = FollowerSerializer(many=True, required=False)
    followed = FollowedSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',
                  'profile', 'liked', 'relations', 'followers', 'followed', 'posts')


class UserPostsSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()
    posts = PostSerializer(source='photos', many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'profile', 'posts')


class AlbumSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Album
        fields = ('id', 'user_id', 'name', 'photos')

    def create(self, validated_data):
        album = Album(**validated_data)
        album.save()
        return album

    def update(self, instance, validated_data):
        album = instance
        if self.partial:
            album.photos.add(*validated_data.get('photos'))
            album.save()
        return album


class AlbumSerializerPhotos(serializers.ModelSerializer):

    class Meta:
        model = Album
        fields = ('id', 'name')


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    photo_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('id', 'user_id', 'photo_id', 'body', 'author_name')

    def create(self, validated_data):
        comment = Comment(**validated_data)
        comment.save()
        return comment


class PhotoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    album_set = AlbumSerializerPhotos(many=True, required=False)
    liked = LikeSerializerPhoto(many=True, required=False)

    class Meta:
        model = Photo
        fields = ('id', 'user_id', 'image', 'description', 'likes', 'album_set', 'liked')

    def create(self, validated_data):
        photo = Photo(**validated_data)
        photo.save()
        return photo


class PhotoUserSerializer(serializers.ModelSerializer):
    user = UserPhotoSerializer()
    comments = CommentPhotoSerializer(many=True, required=False)
    liked = LikeSerializerPhoto(many=True, required=False)

    class Meta:
        model = Photo
        fields = ('id', 'user', 'image', 'description', 'likes', 'liked', 'comments')


class UserRelationSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()
    relations = RelationSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'profile', 'relations')


class RelationSerializerGet(serializers.ModelSerializer):
    user = UserRelationSerializer()

    class Meta:
        model = Relation
        fields = ('id', 'image', 'user')
