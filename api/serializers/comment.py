from rest_framework import serializers

from api.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'author_name', 'user', 'post')
