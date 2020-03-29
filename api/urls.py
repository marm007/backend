from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.filters import PhotoList, CommentListFilter

from rest_framework_simplejwt import views as jwt_views

from api.views.album import AlbumViewSet
from api.views.comment import CommentViewSet
from api.views.follower import FollowerRetrieve
from api.views.post import PostViewSet
from api.views.relation import RelationViewSet
from api.views.user import UsersViewSet, validate_email_token, forgot_password, auth

comments_create = CommentViewSet.as_view({
    'post': 'create',
})

comments_detail = CommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'posts', PostViewSet)
router.register(r'relations', RelationViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [

    path('auth/', auth),
    path('password/reset/<slug:token>/', validate_email_token),
    path('password/forgot/', forgot_password),

    path('comments/<int:pk>/', comments_detail),

    path('posts/<int:pk>/comments/', comments_create),

    path('followers/<int:pk>/', FollowerRetrieve.as_view()),

    # path('photos/filter/', PhotoList.as_view()),
    # path('photos/<int:photo_id>/comments/filter/', CommentList.as_view()),

    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),

]


