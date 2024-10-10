import os


class Config:
    # obtain environment variable - API KEY
    API_KEY = os.getenv('API_KEY')
    # name for db file to store API responses
    response_db_file = os.getenv('response_db_file')
    # flask app SECRET  KEY
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR')
