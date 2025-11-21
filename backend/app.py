from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config
from models import db

from controllers import (
    auth_ns, user_ns, rag_ns, chat_ns,
    component_ns, guardrails_ns, role_ns
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
    
    # Register blueprints
    # Initialize API
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Type in the "Value" input box below: **Bearer &lt;JWT&gt;**'
        }
    }
    
    api = Api(app, title='Enterprise API', version='1.0', doc='/docs', prefix='/api',authorizations=authorizations, security='Bearer Auth')
       
    # Register namespaces
    api.add_namespace(auth_ns)
    api.add_namespace(user_ns)
    api.add_namespace(role_ns)
    api.add_namespace(component_ns)
    api.add_namespace(rag_ns)
    api.add_namespace(chat_ns)
    api.add_namespace(guardrails_ns)
    
    # Initialize database and run migrations
    from migrations.init_db import init_db
    init_db(app)
    
    @app.route('/')
    def index():
        """Health check endpoint"""
        return {
            'status': 'running',
            'message': 'Enterprise Flask Microservice API',
            'version': 'v1'
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
    print(f'🔐 Default Admin: admin@mail.com / password')
    print(f'⚠️  Remember to set GOOGLE_API_KEY in .env file')
    print('='*60 + '\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
