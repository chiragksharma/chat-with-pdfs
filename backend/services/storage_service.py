from google.cloud import storage
from config import Config
import tempfile
import os
import psycopg2
import pickle

bucket_name = "pdf_storage_chirag_ease_ai_868"

metadata_store = {}



def upload_file(file_obj, filename):
    """Uploads a file to the Cloud Storage bucket."""
    client = storage.Client.from_service_account_json(Config.SERVICE_ACCOUNT_KEY_PATH)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file_obj)
    blob.make_public()
    blob.content_type = 'application/pdf'
    blob.content_disposition = 'inline'
    blob.patch()
    return blob.public_url

def store_document_metadata(document_id, metadata,filename):
    """Stores metadata related to the document."""
    # Add your logic to store metadata in a database or any other storage
    # For demonstration purposes, let's print the metadata
    client = storage.Client.from_service_account_json(Config.SERVICE_ACCOUNT_KEY_PATH)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)

    # Set metadata for the uploaded file
    blob.metadata = {
        'document_id': document_id,
        'metadata': metadata
    }

    blob.content_disposition = 'inline'

    blob.patch()
    
    metadata_store[document_id] = metadata

    # Download the file to a temporary path for further processing
    temp_file_path = os.path.join(tempfile.gettempdir(), filename)
    blob.download_to_filename(temp_file_path)
    print(f"Storing metadata for document {document_id}: {metadata}")

    return temp_file_path


