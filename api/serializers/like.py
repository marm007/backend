from rest_framework import serializers

from api.models import Like


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

