from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AddPhoto, UsersViewSet, AddPhotoViewSet

from rest_framework_simplejwt import views as jwt_views


router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'photos', AddPhotoViewSet)

urlpatterns = [
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('photo/add/', AddPhoto.as_view(), name='add_photo'),

    path('', include(router.urls)),

    # path('users/', user_list, name='user-list'),
    # path('users/<int:pk>/', user_detail, name='user-detail')
    # path('users/', UsersList.as_view()),
    # path('users/create', UserCreate.as_view(), name="create_user"),

]


