import psycopg2
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from google.cloud import storage
from config import Config

read_documents = Blueprint('readDocuments', __name__)


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def get_all_document_metadata():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT document_id, title, file_url FROM document_metadata")
    documents = cur.fetchall()
    cur.close()
    conn.close()
    return documents


@read_documents.route("/documents", methods=["GET"])
def get_all_documents():
    
    # Get metadata from PostgreSQL
    document_metadata = get_all_document_metadata()
    
    return jsonify(document_metadata), 200