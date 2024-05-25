import pdfminer
from flask import Blueprint, request, jsonify, current_app
from services.storage_service import upload_file, store_document_metadata
from werkzeug.utils import secure_filename
from pdfquery import PDFQuery
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from transformers import AutoTokenizer, AutoModel
from pinecone import Pinecone, ServerlessSpec
import psycopg2
import torch
import os
from celery_config import celery_app
from dotenv import load_dotenv
import pickle


# Load environment variables from .env file
load_dotenv()

create_bp = Blueprint('create', __name__)
# Initialize Pinecone
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')

pc = Pinecone(api_key=pinecone_api_key)
if pinecone_index_name not in pc.list_indexes().names():
    pc.create_index(
        name=pinecone_index_name,
        dimension=384,  # Adjust dimension based on your embedding model
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region=pinecone_environment
        )
    )
index = pc.Index(pinecone_index_name)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def create_table():
    """Creates the document_embeddings table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS document_embeddings (
        document_id VARCHAR PRIMARY KEY,
        title VARCHAR,
        file_url VARCHAR,
        embeddings BYTEA
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

@celery_app.task(name="routes.create.process_document_task")
def process_document_task(document_id, title, file_url, temp_file_path):
    print(f"Starting to process document {document_id}")
    try:
        # Extract text from the downloaded PDF file
        document_text = extract_text_from_pdf(temp_file_path)
        print(f"Extracted text from document {document_id}")

        # Generate embeddings from the extracted text
        embeddings = generate_embeddings(document_text)
        print(f"Generated embeddings for document {document_id}")

        # Store embeddings in PostgreSQL
        store_embeddings_in_postgres(document_id, title, file_url, embeddings)
        print(f"Stored embeddings for document {document_id}")

        # Clean up temporary file
        os.remove(temp_file_path)
        print(f"Cleaned up temporary file for document {document_id}")
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")


def extract_text_from_pdf(file):
    # Extract text from the PDF file using pdfminer
    text = ""
    for page_layout in extract_pages(file):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text += element.get_text()
    return text


@create_bp.route("/create", methods=["POST"])
def create_document():
    """Handles creating metadata for the document."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    document_id = os.path.splitext(filename)[0]  # Use the filename (without extension) as the document ID

    # Upload the file to Cloud Storage
    try:
        file_url = upload_file(file, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    title = request.form.get('title', '')
    metadata = {
        "title": title,
        "file_url": file_url
    }

    # Store the document metadata
    temp_file_path = store_document_metadata(document_id, metadata,file.filename)
    print(f"Document ID: {document_id}")
    print(f"Title: {title}")
    print(f"File URL: {file_url}")
    print(f"Temp File Path: {temp_file_path}")

    # Send task to Celery
    #process_document_task.delay(document_id, title, file_url, temp_file_path)

    # Extract text from the downloaded PDF file
    document_text = extract_text_from_pdf(temp_file_path)
    print(f"Extracted text from document {document_id}")

    text_segments = split_text_into_segments(document_text)
    

    # Generate embeddings from the extracted text segments
    embeddings = [generate_embeddings(segment) for segment in text_segments]
    print(f"Generated embeddings for document {document_id}")
    
     # Store embeddings in PostgreSQL
    store_embeddings_in_postgres(document_id, title, file_url, embeddings, text_segments)
    print(f"Stored embeddings for document {document_id}")


    os.remove(temp_file_path)


    return jsonify({
        "message": "Document uploaded and metadata stored successfully. Processing in background.",
        "document_id": document_id,
        "file_url": file_url
    }), 200


def generate_embeddings(text):
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    return embeddings


def store_embeddings_in_pinecone(document_id, embeddings):
    index.upsert([(document_id, embeddings.tolist())])

def store_embeddings_in_postgres(document_id, title, file_url, embeddings, texts):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for idx, embedding in enumerate(embeddings):
            serialized_embedding = pickle.dumps(embedding)  # Serialize embedding
            cur.execute("""
                INSERT INTO document_embeddings (document_id, title, file_url, embedding, text, idx)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id, idx) DO UPDATE 
                SET embedding = EXCLUDED.embedding,
                    text = EXCLUDED.text;
            """, (document_id, title, file_url, serialized_embedding, texts[idx], idx))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Document {document_id} successfully inserted/updated.")
    except Exception as e:
        print(f"Error inserting/updating document {document_id}: {e}")



def get_document_metadata(document_id):
    """Fetches metadata for a given document."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, file_url FROM document_embeddings WHERE document_id = %s", (document_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return {"title": result[0], "file_url": result[1]}
    return None


def split_text_into_segments(text, max_length=512):
    """Splits the text into smaller segments to ensure they fit within model limits."""
    words = text.split()
    segments = []
    current_segment = []

    for word in words:
        if len(current_segment) + len(word) + 1 <= max_length:
            current_segment.append(word)
        else:
            segments.append(" ".join(current_segment))
            current_segment = [word]

    if current_segment:
        segments.append(" ".join(current_segment))

    return segments