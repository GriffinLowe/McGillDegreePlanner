import io
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier

def connect_to_blob_storage(

def upload_blob_stream(self, blob_service_client: BlobServiceClient, container_name: str):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="sample-blob.txt")
    input_stream = io.BytesIO(os.urandom(15))
    blob_client.upload_blob(input_stream, blob_type="BlockBlob")
