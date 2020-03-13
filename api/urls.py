from django.urls import path
from .views import CreateUser, HelloWorldView, AddPhoto
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class CustomJWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password'),
            'id': ''
        }

        # This is answering the original question, but do whatever you need here.
        # For example in my case I had to check a different model that stores more user info
        # But in the end, you should obtain the username to continue.
        user_obj = User.objects.filter(email=attrs.get('email')).first()
        if user_obj:
            credentials['id'] = user_obj.id
            print(user_obj.id)

        return super().validate(credentials)

#serializer_class=CustomJWTSerializer),


urlpatterns = [
    path('user/create/', CreateUser.as_view(), name="create_user"),
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('hello/', HelloWorldView.as_view(), name='hello_world'),

    path('photo/add/', AddPhoto.as_view(), name='add_photo')
]
