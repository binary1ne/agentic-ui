from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from models import db
from controllers import (
    auth_bp, user_bp, rag_bp, chat_bp,
    component_bp, guardrails_bp, role_bp
)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize config
    Config.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Initialize API
    api = Api(app)
    
    # Register blueprints
    api.register_blueprint(auth_bp)
    api.register_blueprint(user_bp)
    api.register_blueprint(rag_bp)
    api.register_blueprint(chat_bp)
    api.register_blueprint(component_bp)
    api.register_blueprint(guardrails_bp)
    api.register_blueprint(role_bp)
    # Initialize database and run migrations
    from migrations.init_db import init_db
    init_db(app)
    
    @app.route('/')
    def index():
        """Health check endpoint"""
        return {
            'status': 'running',
            'message': 'Enterprise Flask Microservice API',
            'version': Config.API_VERSION,
            'documentation': '/swagger-ui'
        }
    
    @app.route('/health')
    def health():
        """Health check"""
        return {'status': 'healthy'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    print('\n' + '='*60)
    print('🚀 Enterprise Flask Microservice Starting...')
    print('='*60)
    print(f'📚 API Documentation: http://localhost:5000/swagger-ui')
    print(f'🔐 Default Admin: admin@mail.com / password')
    print(f'⚠️  Remember to set GOOGLE_API_KEY in .env file')
    print('='*60 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
