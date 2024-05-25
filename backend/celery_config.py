# celery_config.py
import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def make_celery(app=None):

    try:
        broker_url = os.getenv('CELERY_BROKER_URL')
        result_backend = os.getenv('CELERY_RESULT_BACKEND')

        if not broker_url:
            raise ValueError("CELERY_BROKER_URL environment variable not set")
        if not result_backend:
            raise ValueError("CELERY_RESULT_BACKEND environment variable not set")

        print("Initializing Celery with broker:", broker_url)
        print("Initializing Celery with result backend:", result_backend)
        celery_app_name = 'pdf_chat_celery'

        celery_app = Celery(
            celery_app_name,
            backend=result_backend,
            broker=broker_url,
            include=['routes.create']  # Add the module containing your tasks
        )
        # Manually define the configuration
        celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],  # Ignore other content
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            # Add other Celery configuration options here
        )
        TaskBase = celery_app.Task

        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                print("Running task in Flask app context")
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery_app.Task = ContextTask

        print("Celery successfully initialized")
        return celery_app
    except Exception as e:
        print(f"Error initializing Celery: {e}")
        raise

celery_app = make_celery()  # Initialize without app to be available for Celery command line
