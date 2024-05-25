from flask import Flask
from routes.upload import upload_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.register_blueprint(upload_bp)

    return app
