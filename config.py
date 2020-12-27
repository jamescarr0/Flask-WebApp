#################################################################
# Application Configuration Settings.
# Add Environment variables to .env file.
#################################################################

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """
    A configuration class to manage environment variables.
    """

    PREFERRED_URL_SCHEME = 'https'
    
    # Number of posts per page
    POSTS_PER_PAGE = 15

    # Source a secret key from the environment, if not found, use hard coded string.
    # CSRF Signing.
    SECRET_KEY = os.environ.get('SECRET_KEY') or ("DEVELOPMENT_KEY_ONLY!_ADD_KEY_TO_ENV_VAR")
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    REGISTRATION_PIN = os.environ.get('REGISTRATION_PIN') or '1111'

    # Source database URI from environment or hardcode path.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_DATABASE_CHARSET = 'utf8mb4'

    # Mail settings.
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER_NAME')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_RESET_PASSWORD_SUBJECT = os.environ.get('MAIL_RESET_PASSWORD_SUBJECT')

    MAIL_RESET_PASSWORD_SIGNATURE = os.environ.get(
        'MAIL_RESET_PASSWORD_SIGNATURE')
    
    ADMINS = [os.environ.get('ADMIN_EMAIL')]
    PERSONAL_EMAIL = [os.environ.get('PERSONAL_EMAIL')]
    CLIENT_EMAIL=[os.environ.get('CLIENT_EMAIL')]

    IMG_UPLOAD_PATH = basedir + '/app/static/uploads'

    MAX_IMG_SIZE = 1024 * 1024
    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

    HTML_CLEAN_ALLOWED_TAGS = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                               'i', 'li', 'ol', 'strong', 'ul', 'p', 'h1', 'h2', 'h3',
                               'h4', 'h5', 'h6', 'span', 'img']

    HTML_CLEAN_ALLOWED_ATTRS = {
        '*': ['style'],
        'a': ['href', 'rel', 'title'],
        'abbr': ['title'],
        'acronym': ['title'],
        'img': ['src', 'alt', 'height', 'width']
    }

    HTML_CLEAN_ALLOWED_STYLES = [
        'color', 'font-weight', 'text-align', 'display', 'margin-left', 'margin-right',
        'margin', 'float', 'display'
    ]

    POST_SNIPPET_LENGTH = 90
    OG_SNIPPET_LENGTH = 90

    WEBSITE_FORM_EMAIL_RECIPIENT = [os.environ.get('PERSONAL_EMAIL')]
    WEBSITE_FORM_SUBJECT = '** NO REPLY **'
