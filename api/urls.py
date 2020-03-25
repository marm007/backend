from django.urls import path, include
from rest_auth.views import PasswordResetView
from rest_framework.routers import DefaultRouter

from api.filters import PhotoList, CommentList
from .views import UsersViewSet, PhotoViewSet, CommentViewSet, AlbumViewSet, auth, reset_password, validate_email_token, \
    RelationViewSet

from rest_framework_simplejwt import views as jwt_views


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

relation_user = UsersViewSet.as_view({
    'get': 'relation',
})

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [

    path('auth/', auth),
    path('users/<int:pk>/relations/', relation_user),
    path('users/password/reset/<slug:token>/', validate_email_token),
    path('users/password/reset/', reset_password),

    path('photos/filter/', PhotoList.as_view()),
    path('photos/<int:photo_id>/comments/filter/', CommentList.as_view()),

    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),

    path('photos/<int:pk>/comments/', comments_list),

    path('comments/<int:pk>/', comments_detail),

]


