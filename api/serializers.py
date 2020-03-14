from rest_framework import serializers
from api.models import User, UserProfile, Photo
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('photo',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        print("dauser")
        print(user)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.photo = profile_data.get('photo', profile.photo)
        profile.save()

        return instance


class PhotoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Photo
        fields = ('user_id', 'image', 'name')

    def create(self, validated_data):
        print("dauseadaddr")
        print(validated_data)

        photo = Photo(**validated_data)
        photo.save()
        return photo
