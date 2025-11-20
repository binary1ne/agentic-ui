import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    
    # API Configuration
    API_TITLE = 'Enterprise Flask Microservice'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:4200', 'http://127.0.0.1:4200']
    
    # Google Gemini
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
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(Config.DOCUMENTS_PATH, exist_ok=True)
