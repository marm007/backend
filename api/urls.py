from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.filters import PhotoList, CommentList
from .views import UsersViewSet, PhotoViewSet, CommentViewSet, AlbumViewSet

from rest_framework_simplejwt import views as jwt_views

comment_create = CommentViewSet.as_view({
    'post': 'create'
})

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [

    path('photos/filter/', PhotoList.as_view()),
    path('comments/filter/', CommentList.as_view()),

    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),

    path('comments/<int:pk>/', comment_create),

]


