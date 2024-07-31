from django.urls import path
from .views import GetPhotos, login, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('login/', login, name='login'),
    path('getphotos/', GetPhotos.as_view(), name='getphotos'),
]
