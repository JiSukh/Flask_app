import os
from dotenv import load_dotenv



# captcha keys
# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # General settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ADMIN_FLUID_LAYOUT = os.getenv('FLASK_ADMIN_FLUID_LAYOUT') == 'True'

    # Rate limiting settings
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT')

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO') == 'True'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

    # Captcha keys
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_API_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_API_KEY')

    # Logging configuration
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH')

    # Maximum login attempts
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS'))
