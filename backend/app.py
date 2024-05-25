from flask import Flask
from dotenv import load_dotenv
from urllib.parse import quote
from routes.upload import upload_bp
from routes.create import create_bp
from routes.getfiles import read_file_bp
from routes.chat import chat_bp
from routes.readfiles import read_documents
from config import Config
from flask_cors import CORS
from google.cloud import storage
from celery_config import make_celery
import os


load_dotenv()



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(upload_bp)
    app.register_blueprint(create_bp)
    app.register_blueprint(read_file_bp,url_prefix='/read')
    app.register_blueprint(read_documents)
    app.register_blueprint(chat_bp,url_prefix='/document_chat')



    client = storage.Client.from_service_account_json(Config.SERVICE_ACCOUNT_KEY_PATH)

    # Add the storage client to the Flask app context for easy access in routes
    app.storage_client = client

    # Initialize Celery
    app.celery_app = make_celery(app)


    return app

app = create_app()
CORS(app)



if __name__ == "__main__":
    app.run(debug=True)