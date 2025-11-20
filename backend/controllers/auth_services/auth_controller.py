from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from services import AuthService
from dtos.auth_data.auth_data import (
    LoginSchema, SignupSchema, UserResponseSchema, CheckEmailSchema,
    AuthResponseSchema, CheckEmailResponseSchema
)

# Create blueprint
auth_bp = SmoreBlueprint(
    'auth',
    __name__,
    url_prefix='/api/auth',
    description='Authentication endpoints'
)


# Routes
@auth_bp.route('/check-email')
class CheckEmailView(MethodView):
    @auth_bp.arguments(CheckEmailSchema)
    @auth_bp.response(200, CheckEmailResponseSchema)
    def post(self, data):
        """Check if email exists and get role"""
        try:
            result = AuthService.check_user_exists(data['email'])
            return result
        except Exception as e:
            abort(500, message=str(e))

@auth_bp.route('/signup')
class SignupView(MethodView):
    @auth_bp.arguments(SignupSchema)
    @auth_bp.response(201, AuthResponseSchema)
    def post(self, data):
        """User registration"""
        try:
            # Check if signup is enabled
            from models import SystemConfig
            config = SystemConfig.query.get('signup_enabled')
            if config and config.value.lower() != 'true':
                # Check if it's the first user (admin) - allow if no users exist
                from models import User
                if User.query.count() > 0:
                    abort(403, message="Public registration is currently disabled. Please contact an administrator.")

            result = AuthService.register_user(
                email=data['email'],
                password=data['password'],
                role=data.get('role', 'user'),
                full_name=data.get('full_name')
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'Registration failed: {str(e)}')

@auth_bp.route('/login')
class LoginView(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, AuthResponseSchema)
    def post(self, data):
        """User login"""
        try:
            result = AuthService.login_user(
                email=data['email'],
                password=data['password'],
                role=data.get('role')
            )
            return result
        except ValueError as e:
            abort(401, message=str(e))
        except Exception as e:
            abort(500, message=f'Login failed: {str(e)}')

@auth_bp.route('/me')
class MeView(MethodView):
    @jwt_required()
    @auth_bp.response(200, UserResponseSchema)
    def get(self):
        """Get current user"""
        try:
            user = AuthService.get_current_user()
            return user.to_dict()
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=f'Failed to get user: {str(e)}')

@auth_bp.route('/config/signup')
class SignupConfigView(MethodView):
    def get(self):
        """Get signup configuration"""
        try:
            from models import SystemConfig
            config = SystemConfig.query.get('signup_enabled')
            return {'enabled': config.value.lower() == 'true' if config else True}
        except Exception as e:
            abort(500, message=str(e))

    @jwt_required()
    def post(self):
        """Update signup configuration (Admin only)"""
        try:
            user = AuthService.get_current_user()
            if not user.is_admin():
                abort(403, message="Admin access required")
            
            data = request.get_json()
            enabled = data.get('enabled', True)
            
            from models import SystemConfig, db
            config = SystemConfig.query.get('signup_enabled')
            if not config:
                config = SystemConfig(key='signup_enabled', description='Enable or disable public user registration')
                db.session.add(config)
            
            config.value = str(enabled).lower()
            db.session.commit()
            
            return {'enabled': config.value == 'true', 'message': 'Configuration updated'}
        except Exception as e:
            abort(500, message=str(e))
