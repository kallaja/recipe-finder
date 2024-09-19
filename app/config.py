import os


class Config:
    # obtain environment variable - API KEY
    API_KEY = os.getenv('API_KEY')

    db_file = 'database.db'
