from django.urls import path
from .views import GetPhotos, index, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('index/', index, name='index'),
    path('get-photos/', GetPhotos.as_view(), name='get_photos'),
]
