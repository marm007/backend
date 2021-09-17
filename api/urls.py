from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.models import Token
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

from api.filters import UsersFilterList
from api.views.auth import (activate_account_link_clicked, auth,
                            forgot_password, logout, recaptcha_validate,
                            reset_password)
from api.views.comment import CommentViewSet
from api.views.me import (UserMeListFollowedPosts, UserMeListFollowedRelations,
                          UserMeRetrieve, dashboard)
from api.views.post import PostViewSet
from api.views.relation import RelationViewSet
from api.views.user import (UserListPostsProfile, UserRetrieveProfile,
                            UsersViewSet)

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

urlpatterns = [



    path('auth/', auth),
    path('logout/', logout),
    path('recaptcha_validate/', recaptcha_validate),
    path('password/reset/<slug:token>/', reset_password),
    path('password/forgot/', forgot_password),
    path('activate/', activate_account_link_clicked),

    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(),
         name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('comments/<uuid:pk>/', comments_detail),

    path('posts/<uuid:pk>/comments/', comments_create),


    path('users/<uuid:pk>/posts/', UserListPostsProfile.as_view()),
    path('users/<uuid:pk>/profile/', UserRetrieveProfile.as_view()),

    path('users/me/', UserMeRetrieve.as_view()),
    path('users/me/dashboard/', dashboard),
    path('users/me/followed/posts/', UserMeListFollowedPosts.as_view()),
    path('users/me/followed/relations/', UserMeListFollowedRelations.as_view()),

    path('users/filter/', UsersFilterList.as_view()),
    path('', include(router.urls)),

]


admin.site.unregister(Token)
