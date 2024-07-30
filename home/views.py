import uuid
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from home.models import Image
from utils.azure_blob import AzureBlobService
from rest_framework.reverse import reverse



@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'index': reverse('index', request=request, format=format),
        'getphotos': reverse('getphotos', request=request, format=format),
    })

@api_view(['GET','POST'])
def index(request):
    return Response("Hello world")

class GetPhotos(APIView):
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
                image_url = photo['src']['original']
                photographer = photo['photographer']

                image_data = requests.get(image_url).content
                unique_id = uuid.uuid4()
                blob_name = f"{photographer}/{unique_id}.jpg"
                blob_url = azure_service.upload_data(image_data, blob_name)

                photo['url'] = blob_url
                photo['src']['original'] = blob_url

                # Veritabanı kaydı kontrolü
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
