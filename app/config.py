import os


class Config:
    # obtain environment variable - API KEY
    API_KEY = os.getenv('API_KEY')
    # name for db file to store API responses
    db_file = 'response.db'
    # flask app SECRET  KEY
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
