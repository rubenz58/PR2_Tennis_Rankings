import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key"
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.environ.get("JWT_SECRET")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
