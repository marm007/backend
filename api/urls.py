from django.urls import path

from .views import CreateUser, HelloWorldView, AddPhoto, UserList
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('user/create/', CreateUser.as_view(), name="create_user"),
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('hello/', HelloWorldView.as_view(), name='hello_world'),

    path('photo/add/', AddPhoto.as_view(), name='add_photo'),

    path('users/', UserList.as_view())

]


