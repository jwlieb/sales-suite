import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///salessuite.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Amazon SP-API
    AMAZON_REFRESH_TOKEN = os.getenv('AMAZON_REFRESH_TOKEN')
    AMAZON_CLIENT_ID = os.getenv('AMAZON_CLIENT_ID')
    AMAZON_CLIENT_SECRET = os.getenv('AMAZON_CLIENT_SECRET')
    AMAZON_AWS_ACCESS_KEY = os.getenv('AMAZON_AWS_ACCESS_KEY')
    AMAZON_AWS_SECRET_KEY = os.getenv('AMAZON_AWS_SECRET_KEY')
    AMAZON_ROLE_ARN = os.getenv('AMAZON_ROLE_ARN')
    AMAZON_MARKETPLACE_ID = os.getenv('AMAZON_MARKETPLACE_ID')
