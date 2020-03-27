from rest_framework import serializers

from api.models import Follower, User


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
