from rest_framework import serializers

from api.models import Relation, UserMeta, User


#
# class UserSerializer(serializers.ModelSerializer):
#     profile = UserProfileSerializer(read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'profile')


class RelationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class RelationSerializer(serializers.ModelSerializer):
    user = RelationUserSerializer(required=False)

    class Meta:
        model = Relation
        fields = ('id', 'image', 'user', 'created')

