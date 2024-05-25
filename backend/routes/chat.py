from transformers import AutoTokenizer,AutoModel ,AutoModelForSequenceClassification
from flask import Blueprint, request, jsonify
import torch
import os
import psycopg2
from dotenv import load_dotenv
from config import Config
import openai
import pickle
import numpy as np
from services.llm_api import APIClient





chat_bp = Blueprint('chat', __name__)


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(os.getenv('DATABASE_URL'))


@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    document_id = data.get('document_id')
    print("User Message:",user_message)
    print("document_id: ", document_id)

    if not user_message or not document_id:
        return jsonify({"error": "Message and document ID are required"}), 400

    try:
        # Convert user message to embeddings
        user_embedding = generate_embeddings(user_message)

        # Retrieve document embeddings
        document_embeddings = get_document_embeddings(document_id)
        print("Document embeddings:",document_embeddings)

        if document_embeddings is None:
            return jsonify({"error": "Document not found"}), 404

        # Find the most relevant content in the document
        relevant_text = find_relevant_text(document_id, user_embedding, document_embeddings)
        print("Relevant text: ",relevant_text)
        print("User Message: ",user_message)
        # Interact with the LLM API (e.g., OpenAI's GPT-3/4)
        llm_response = interact_with_llm(relevant_text,user_message)

        # Store the chat messages
        store_chat_message(document_id, user_message, llm_response)

        return jsonify({"response": llm_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def generate_embeddings(text):
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings

def get_document_embeddings(document_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT embedding FROM document_embeddings WHERE document_id = %s", (str(document_id),))
        result = cur.fetchone()
        if result and result[0] is not None:
            # Assuming the embeddings are stored as a binary blob
            serialized_embedding = result[0]
            embeddings = pickle.loads(serialized_embedding)
            if isinstance(embeddings, np.ndarray):
                return torch.tensor(embeddings)
            else:
                raise ValueError("Retrieved embeddings are not in the expected format")
        else:
            print(f"No embeddings found for document ID: {document_id}")
            return None
    except Exception as e:
        print(f"Error retrieving document embeddings: {e}")
        return None
    finally:
        cur.close()
        conn.close()
        

def find_relevant_text(document_id, user_embedding, document_embeddings):
    # Ensure user_embedding and document_embeddings are tensors
    if isinstance(user_embedding, np.ndarray):
        user_embedding = torch.tensor(user_embedding)
    if isinstance(document_embeddings, np.ndarray):
        document_embeddings = torch.tensor(document_embeddings)

    # Add an extra dimension to user_embedding to match dimensions for cosine similarity
    user_embedding = user_embedding.unsqueeze(0)

    # Calculate cosine similarities
    similarities = torch.nn.functional.cosine_similarity(user_embedding, document_embeddings)

    # Find the index of the most similar embedding
    max_similarity_idx = torch.argmax(similarities).item()

    # Extract the relevant text based on the embedding index
    relevant_text = extract_text_from_embedding_idx(document_id, max_similarity_idx)
    return relevant_text


def store_chat_message(document_id, user_message, llm_response):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chat_messages (document_id, user_message, llm_response)
            VALUES (%s, %s, %s);
        """, (document_id, user_message, llm_response))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error storing chat message: {e}")


def interact_with_llm(text,user_message):
    prompt = f"Context: {text}\n\nQuestion:{user_message} "
    response = APIClient.generate_chat_completion(prompt)
    return response

def extract_text_from_embedding_idx(document_id, idx):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT text FROM document_embeddings WHERE document_id = %s AND idx = %s", (document_id, idx))
        result = cur.fetchone()
    except Exception as e:
        print(f"Error retrieving text for document ID {document_id} at index {idx}: {e}")
        result = None
    finally:
        cur.close()
        conn.close()

    if result:
        return result[0]
    return None