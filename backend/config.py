from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SERVICE_ACCOUNT_KEY_PATH = "./service_account_key.json"

    # Add more configuration settings as needed