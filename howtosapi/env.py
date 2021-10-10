import os
from dotenv import load_dotenv


class cAppSettings:
    def __init__(self):
        load_dotenv()
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.DEBUG = self.get_bool_env('DEBUG')
        self.ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
        self.MEDIA_ROOT = os.getenv('MEDIA_ROOT')
        self.MEDIA_URL = os.getenv('MEDIA_URL')
        self.SECURE_SSL_REDIRECT = self.get_bool_env('SECURE_SSL_REDIRECT')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASS = os.getenv('DB_PASS')
        self.DB_HOST = os.getenv('DB_HOST')

    def get_bool_env(self, variable_name):
        if not os.getenv(variable_name):
            raise ImportError(f'Variable name "{variable_name}" not found in .env')

        var = os.getenv(variable_name).lower()

        if (var == 'true'): return True
        if (var == 'false'): return False
        raise AttributeError('Environment variable does not equal to either true or false')