from flask import Blueprint, request, jsonify
from services.storage_service import upload_file

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload():
    """Handles file upload requests."""
    file = request.files["file"]
    if file:
        file_url = upload_file(file, file.filename)
        return jsonify({"file_url": file_url}), 200
    else:
        return jsonify({"error": "No file uploaded"}), 400
