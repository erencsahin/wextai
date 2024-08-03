import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from home.serializer import CustomUserSerializer, LoginSerializer, RegisterSerializer
from home.models import CustomUser, Image
from utils.azure_blob import AzureBlobService
from rest_framework.reverse import reverse
from rest_framework import status,permissions

from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'login': reverse('login', request=request, format=format),
        'getphotos': reverse('getphotos', request=request, format=format),
        'register': reverse('register', request=request, format=format)
    })

class register(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class userdetail(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class GetPhotos(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"error": "Query parameter is required"}, status=400)

        api_url = f"https://api.pexels.com/v1/search?query={query}"
        headers = {
            "Authorization": settings.MY_API_KEY
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            azure_service = AzureBlobService()
            for photo in data.get('photos', []):
                photo_id = photo['id']
                blob_name = f"{query}/{photo_id}.jpg"

                if azure_service.check_blob_exists(blob_name):
                    blob_url = azure_service.get_blob_url(blob_name)
                    photo['url'] = blob_url
                    photo['src'] = { 'original','large2x','large','medium','small','portrait','landscape','tiny'}.add(blob_url)
                else:
                    image_url = photo['src']['original']
                    image_data = requests.get(image_url).content

                    blob_url = azure_service.upload_data(image_data, blob_name)

                    photo['url'] = blob_url
                    photo['src'] = { 'original','large2x','large','medium','small','portrait','landscape','tiny'}.add(blob_url)

                    image_record = Image(photographer=photo['photographer'], url=blob_url)
                    image_record.save()
            return Response(data)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=400)
