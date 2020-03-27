from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.filters import PhotoList, CommentList

from rest_framework_simplejwt import views as jwt_views

from api.views.album import AlbumViewSet
from api.views.comment import CommentViewSet
from api.views.follower import FollowerViewSet
from api.views.post import PostViewSet
from api.views.relation import RelationViewSet
from api.views.user import UsersViewSet, validate_email_token, forgot_password, auth

comments_list = CommentViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

comments_detail = CommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_relations = UsersViewSet.as_view({
    'get': 'get_relations',
})

user_posts = UsersViewSet.as_view({
    'get': 'get_posts',
})

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'photos', PostViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'relations', RelationViewSet)
router.register(r'followers', FollowerViewSet)

urlpatterns = [

    path('auth/', auth),
    path('users/<int:pk>/relations/', user_relations),
    path('users/<int:pk>/posts/', user_posts),
    path('users/password/reset/<slug:token>/', validate_email_token),
    path('users/password/forgot/', forgot_password),

    path('photos/filter/', PhotoList.as_view()),
    path('photos/<int:photo_id>/comments/filter/', CommentList.as_view()),

    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),

    path('photos/<int:pk>/comments/', comments_list),

    path('comments/<int:pk>/', comments_detail),

]


