from api.models import Post, Relation, User
from api.serializers.post import PostSerializer
from api.serializers.relation import RelationSerializer
from api.serializers.user import UserMetaSerializer
from django.db.models.query_utils import Q
from rest_framework import serializers


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DashboardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    posts = serializers.SerializerMethodField()
    relations = serializers.SerializerMethodField()
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'posts', 'relations', 'meta')

    def get_posts(self, instance):
        posts = Post.objects.filter(Q(user=instance) | Q(
            user__followers__user__id=instance.id)).distinct().order_by('-created')[:12]
        serialized = PostSerializer(instance=posts, many=True, context={
                                    'request': dotdict({'user': instance})})
        return serialized.data

    def get_relations(self, instance):
        relations = Relation.timeframed.filter(Q(user=instance) | Q(
            user__followers__user__id=instance.id)).distinct().order_by('created')[:12]
        serialized = RelationSerializer(instance=relations, many=True)
        return serialized.data
