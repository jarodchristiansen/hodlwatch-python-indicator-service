"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
CRYPTO_COMPARE_KEY = environ.get('CRYPTO_COMPARE_KEY')
INIDCATOR_SERVER_KEY = environ.get('INIDCATOR_SERVER_KEY')
