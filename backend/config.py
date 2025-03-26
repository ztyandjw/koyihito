import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = os.environ.get('PORT') or 8000
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///./test.db'