from azure.storage.blob import BlobServiceClient

from core import settings

class AzureBlobService:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING_DEV)
        self.container_name = 'wext-ai-images'

    def upload_data(self, data, blob_name):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.upload_blob(data)
        return blob_client.url
