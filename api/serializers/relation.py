from rest_framework import serializers

from api.models import Relation, RelationMeta, UserMeta, User


class UserMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserMeta
        fields = ('avatar',)

    def get_avatar(self, instance):
        if instance.avatar:
            instance.avatar.url_options.update({'secure': True})
            return instance.avatar.url
        else:
            return 'https://res.cloudinary.com/marm007/image/upload/v1585912225/avatar_iahjs2.png'


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    meta = UserMetaSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'meta')


class RelationMetaSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    relation = serializers.PrimaryKeyRelatedField

    class Meta:
        model = RelationMeta
        fields = '__all__'

    def create(self, validated_data):
        return RelationMeta.objects.create(**validated_data)


class RelationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField
    user = UserSerializer(read_only=True)
    image_meta = serializers.SerializerMethodField()

    class Meta:
        model = Relation
        fields = ('id', 'image', 'created', 'user', 'image_meta')
        extra_kwargs = {
            'image': {'write_only': True}
        }

    def create(self, validated_data):
        relation = Relation(**validated_data)
        relation.save()
        image_metadata = relation.image_metadata()
        image_metadata['relation'] = relation.id
        serializer = RelationMetaSerializer(data=image_metadata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return relation

    def get_image_meta(self, instance):
        meta = {}
        try:
            meta['width'] = instance.meta.width
            meta['height'] = instance.meta.height
            instance.image.url_options.update({'secure': True})
            meta['url'] = instance.image.url
        except Exception as e:
            print(e)
        return meta
