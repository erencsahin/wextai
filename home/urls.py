from django.urls import path
from .views import CsvFileUpload, login, api_root, register, getPhotos, SaveSelectedPhoto
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)



urlpatterns = [
    path('', api_root, name='api-root'),
    path('login/', login.as_view(), name='login'),
    path('register/',register.as_view(),name='register'),
    path('userdetail/',register.as_view(),name='userdetail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('csvfileupload/',CsvFileUpload.as_view(),name='csvfileupload'),
    path('getphotos/',getPhotos.as_view(),name='getPhotos'),
    path('saveselectedphoto/',SaveSelectedPhoto.as_view(),name='savephoto'),
]
