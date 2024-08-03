from django.urls import path
from .views import GetPhotos, login, api_root, register
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)



urlpatterns = [
    path('', api_root, name='api-root'),
    path('login/', login.as_view(), name='login'),
    path('getphotos/', GetPhotos.as_view(), name='getphotos'),
    path('register/',register.as_view(),name='register'),
    path('userdetail/',register.as_view(),name='userdetail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
]
