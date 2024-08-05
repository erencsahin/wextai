import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from home.serializer import CustomUserSerializer, LoginSerializer, RegisterSerializer, SelectedPhotoSerializer
from home.models import CustomUser, Image
from utils.azure_blob import AzureBlobService
from rest_framework.reverse import reverse
from rest_framework import status,permissions
import csv
from rest_framework.parsers import MultiPartParser, FormParser

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

class CsvFileUpload(APIView):
    parser_classes=(MultiPartParser,FormParser)
    permission_classes=[IsAuthenticated]

    def post(self,request,*args,**kwargs):
        file=request.FILES.get('file')
        if not file:
            return Response({"error":"no file uploaded."})
        
        try:
            decoded_file=file.read().decode('utf-8').splitlines()
            reader=csv.DictReader(decoded_file)
            queries = []
            for row in reader:
                if 'query' in row:
                    queries.append(row['query'])
            if not queries:
                return Response({"error": "No queries found in the file."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'queries':queries},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)})

class getPhotos(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request,*args, **kwargs):
        queries=request.data.get('queries',[])
        if not queries:
            return Response({"error":"No query"},status=status.HTTP_400_BAD_REQUEST)
        photos=[]
        for query in queries:
            api_url=f"https://api.pexels.com/v1/search?query={query}&per_page=2"
            headers={
                "Authorization":settings.MY_API_KEY
            }
            response=requests.get(api_url,headers=headers)
            if response.status_code==200:
                photos_data=response.json().get('photos',[])
                for photo in photos_data:
                    photos.append({
                        'query':query,
                        'photo_url':photo['src']['original'],
                        'photographer':photo['photographer']
                    })
        
        return Response(photos,status=status.HTTP_200_OK)
    
class SaveSelectedPhoto(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SelectedPhotoSerializer(data=request.data)
        if serializer.is_valid():
            azure_service = AzureBlobService()
            photo_url = serializer.validated_data['photo_url']
            query = serializer.validated_data['query']
            photographer = serializer.validated_data['photographer']
            
            image_data = requests.get(photo_url).content
            photo_id = photo_url.split('/')[-1].split('.')[0]
            blob_name = f"{query}/{photo_id}.jpg"

            if Image.objects.filter(url__icontains=blob_name).exists():
                return Response({"message": "Photo already exists", "blob_url": blob_name}, status=status.HTTP_200_OK)
            
            blob_url = azure_service.upload_data(image_data, blob_name)
            
            image_record = Image(photographer=photographer, url=blob_url)
            image_record.save()
            
            return Response({"message": "Photo saved successfully", "blob_url": blob_url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
