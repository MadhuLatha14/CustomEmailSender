import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    CELERY_BROKER_URL = os.getenv("REDIS_URL")  # Using Redis for Celery
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")
