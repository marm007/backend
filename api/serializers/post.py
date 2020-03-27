from rest_framework import serializers

from api.models import Post
from api.serializers.album import AlbumSerializer
from api.serializers.like import LikeSerializer


class PostSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    album_set = AlbumSerializer(many=True, required=False)
    liked = LikeSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('id', 'user_id', 'image', 'description', 'likes', 'album_set', 'liked')

#
# class PostUserSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     comments = CommentSerializer(many=True, required=False)
#     liked = LikeSerializer(many=True, required=False)
#
#     class Meta:
#         model = Post
#         fields = ('id', 'user', 'image', 'description', 'likes', 'liked', 'comments')
