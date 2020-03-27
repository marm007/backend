from rest_framework import serializers

from api.models import Album


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
