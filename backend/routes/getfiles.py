from flask import Blueprint, request, jsonify
from routes.create import get_document_metadata

read_file_bp = Blueprint('readfile', __name__)

@read_file_bp.route("/documents/<document_id>", methods=["GET"])
def get_document(document_id):
    """Handles fetching metadata and file details for a document."""
    metadata = get_document_metadata(document_id)
    if metadata:
        return jsonify({"document_id": document_id, "metadata": metadata}), 200
    else:
        return jsonify({"error": "Document not found"}), 404
