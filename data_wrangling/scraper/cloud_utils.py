import io
import os
import json
from azure.storage.blob import BlobServiceClient

def upload_blob_stream(blob_service_client: BlobServiceClient, container_name: str, source_url: str, source_html: str, blob_name: str):
    """
    Uploads HTML content and its source URL as a JSON object to Azure Blob Storage using an in-memory byte stream.

    This function is intended for single-use or internal workflows, where scraped HTML data and its originating
    link need to be persisted in the cloud. The function creates a JSON object containing the source URL and
    HTML content, writes it to an in-memory byte stream, and uploads it to the specified blob container.

    Parameters
    ----------
    blob_service_client : BlobServiceClient
        An authenticated instance of the Azure BlobServiceClient.
    container_name : str
        The name of the Azure blob container to upload to.
    source_url : str
        The URL from which the HTML content was retrieved.
    source_html : str
        The raw HTML string content to store.
    blob_name : str
        The name of the blob (file) to create or overwrite in the container.

    Returns
    -------
    None
    """
    
    # Create JSON string:
    data = {"link": source_url,
            "html": source_html}
    json_data = json.dumps(data)

    # Establish connection to Azure blob storage: 
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload to blob store
    input_stream = io.BytesIO(json_data.encode('utf-8'))
    blob_client.upload_blob(input_stream, blob_type="BlockBlob", overwrite=True)
