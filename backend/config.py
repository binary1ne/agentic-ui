import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    #JWT
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', '')
    JWT_TOKEN_LOCATION=["headers","cookies"]
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=0,minutes=20)

    #Database
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI', '')
    SQLALCHEMY_TRACK_MODIFICATIONS=False 


    # API Configuration
    API_TITLE = 'Enterprise Flask Microservice'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:4200', 'http://127.0.0.1:4200']
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = 'gpt-4o'
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', '')
    
    # Google Gemini (Deprecated)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GEMINI_MODEL = 'gemini-2.0-flash-exp'
    
    # Brave Search
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', '')
    
    # Vector Database
    CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './data/chroma')
    DOCUMENTS_PATH = os.getenv('DOCUMENTS_PATH', './data/documents')
    
    # Guardrails
    GUARDRAILS_ENABLED = os.getenv('GUARDRAILS_ENABLED', 'True') == 'True'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc', 'md'}

    # SMTP Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_SENDER_EMAIL = os.getenv('SMTP_SENDER_EMAIL', '')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(Config.DOCUMENTS_PATH, exist_ok=True)
