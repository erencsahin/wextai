import uuid
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from home.serializer import LoginSerializer, RegisterSerializer
from django.conf import settings
from home.models import Image
from utils.azure_blob import AzureBlobService
from rest_framework.reverse import reverse
from rest_framework import status

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token







@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'login': reverse('login', request=request, format=format),
        'getphotos': reverse('getphotos', request=request, format=format),
        'register':reverse('register',request=request,format=format)
    })


class register(APIView):
    def post(self,request):
        data=request.data
        serializer=RegisterSerializer(data=data)

        if not serializer.is_valid():
            return Response({
                'status':False,
                'message':serializer.errors
            },  status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response({
            'status':True,
            'message':'user created'
            },status.HTTP_201_CREATED)



class login(APIView):
    def post(self,request):
        data=request.data
        serializer=LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'status':False,
                'message':serializer.errors
            },  status.HTTP_400_BAD_REQUEST)
        

        user=authenticate(username=serializer.data['username'], password=serializer.data['password'])
        if user is not None:
            token, _ =Token.objects.get_or_create(user=user)
            return Response({
                'status': True,
                'message': 'Login successful',
                'token': str(token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': False,
                'message': 'Invalid Username or Password!'
            }, status=status.HTTP_401_UNAUTHORIZED)
        

class GetPhotos(APIView):
    def get(self,request):
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
                image_url = photo['src']['original']
                photographer = photo['photographer']

                image_data = requests.get(image_url).content
                unique_id = uuid.uuid4()
                blob_name = f"{photographer}/{unique_id}.jpg"
                blob_url = azure_service.upload_data(image_data, blob_name)

                photo['url'] = blob_url
                photo['src']['original'] = blob_url

                image_record = Image(photographer=photographer, url=blob_url)
                try:
                    image_record.save()
                except Exception as db_error:
                    return Response({"error": f"Database save error: {str(db_error)}"}, status=500)

            return Response(data)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An error occurred"}, status=500)
        
    
