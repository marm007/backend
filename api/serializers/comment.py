from rest_framework import serializers

from api.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    photo_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('id', 'user_id', 'photo_id', 'body', 'author_name')

