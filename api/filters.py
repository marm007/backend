import django_filters
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import generics
from rest_framework.permissions import AllowAny

from api.models import Post, Comment


# Utworzenie filtra pozwalającego na filtrowanie zdjęć ze względu na:
# like wartość większe od podanej w zapytaniu
# user_id takie jak w zapytaniu
# description zawartośći opsiu zdjęcia
from api.serializers.comment import CommentSerializer
from api.serializers.post import PostSerializer


class PhotoFilter(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            'likes': ['gt', ],
            'user_id': ['exact', ],
            'description': ['contains']
        }


class PhotoList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PhotoFilter


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            'author_name': ['exact', ],
            'created': ['gt', 'lt'],
            'body': ['contains', ]
        }


class CommentList(generics.ListAPIView):

    permission_classes = (AllowAny,)

    def get_queryset(self):
        photo_id = self.kwargs.get('photo_id')
        print(photo_id)
        return Comment.objects.filter(photo=photo_id)

    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
