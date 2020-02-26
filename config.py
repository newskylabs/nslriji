
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env/variables'))


class Config(object):

    # Secret key - should be taken from the environment variable
    # SECRET_KEY in production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very-very-secret-indeed'

    # Location of the application database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # No need to notify the application
    # every time a change is about to be made in the database.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email server details
    MAIL_SERVER    = os.environ.get('MAIL_SERVER')
    MAIL_PORT      = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS   = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME  = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD  = os.environ.get('MAIL_PASSWORD')
    ADMINS         = ['error@formgames.com']

    # Supported languages
    LANGUAGES = ['en', 'es']

    # Translation API
    # When using the MS translation service:
    #| MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    # When using the google translation API:
    GOOGLE_TRANSLATION_PROJECT_ID  = os.environ.get('GOOGLE_TRANSLATION_PROJECT_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    # Elasticsearch
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    # Page layout
    POSTS_PER_PAGE = 10

## fin.
