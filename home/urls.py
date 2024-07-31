from django.urls import path
from .views import GetPhotos, login, api_root, register

urlpatterns = [
    path('', api_root, name='api-root'),
    path('login/', login.as_view(), name='login'),
    path('getphotos/', GetPhotos.as_view(), name='getphotos'),
    path('register/',register.as_view(),name='register'),
]
