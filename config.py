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
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_random_secret_key')
    FLASK_ADMIN_FLUID_LAYOUT = True

    # Rate limiting settings
    RATELIMIT_DEFAULT = "20 per minute; 500 per day"
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///csc2031blog.db')
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Captcha keys (from environment variables)
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_API_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_API_KEY')

    # Logging configuration
    LOG_FILE_PATH = './log/logs.log'

    # Maximum login attempts
    MAX_LOGIN_ATTEMPTS = 3



