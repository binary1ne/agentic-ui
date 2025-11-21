from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from services.auth_services.auth_service import AuthService
from utils.marshmallow_utils import marshmallow_to_restx_model
from dtos.auth_data.auth_data import (
    LoginSchema, SignupSchema, UserResponseSchema, CheckEmailSchema,
    AuthResponseSchema, CheckEmailResponseSchema, SignupConfigSchema
)
from dtos.auth_data.otp_data import VerifyOtpSchema

auth_ns = Namespace('auth', description='Authentication operations')

# Models for Swagger generated from Marshmallow Schemas
check_email_model = marshmallow_to_restx_model(auth_ns, CheckEmailSchema)
signup_model = marshmallow_to_restx_model(auth_ns, SignupSchema)
login_model = marshmallow_to_restx_model(auth_ns, LoginSchema)
verify_otp_model = marshmallow_to_restx_model(auth_ns, VerifyOtpSchema)
signup_config_model = marshmallow_to_restx_model(auth_ns, SignupConfigSchema)
check_email_response_model = marshmallow_to_restx_model(auth_ns, CheckEmailResponseSchema)
auth_response_model = marshmallow_to_restx_model(auth_ns, AuthResponseSchema)
user_response_model = marshmallow_to_restx_model(auth_ns, UserResponseSchema)

@auth_ns.route('/check-email')
class CheckEmail(Resource):
    @auth_ns.expect(check_email_model)
    @auth_ns.doc('check_email')
    @auth_ns.marshal_with(check_email_response_model)
    def post(self):
        """Check if email exists and get role"""
        try:
            data = CheckEmailSchema().load(request.get_json())
            result = AuthService.check_user_exists(data['email'])
            result = AuthService.check_user_exists(data['email'])
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 400

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.doc('signup')
    @auth_ns.marshal_with(auth_response_model, code=201)
    def post(self):
        """User registration"""
        try:
            data = SignupSchema().load(request.get_json())
            
            # Check if signup is enabled
            from models import SystemConfig, UserDetailsModel
            config = SystemConfig.query.get('signup_enabled')
            if config and config.value.lower() != 'true':
                if UserDetailsModel.query.count() > 0:
                    return {"message": "Public registration is currently disabled. Please contact an administrator."}, 403

            result = AuthService.register_user(
                email=data['email'],
                password=data['password'],
                role=data.get('role', 'user'),
                full_name=data.get('full_name')
            )
            return result, 201
        except Exception as e:
            return {'message': str(e)}, 400

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login')
    def post(self):
        """User login"""
        try:
            data = LoginSchema().load(request.get_json())
            result = AuthService.login_user(
                email=data['email'],
                password=data['password'],
                role=data.get('role')
            )
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 401

@auth_ns.route('/verify-otp')
class VerifyOtp(Resource):
    @auth_ns.expect(verify_otp_model)
    @auth_ns.doc('verify_otp')
    def post(self):
        """Verify OTP for 2FA"""
        try:
            data = VerifyOtpSchema().load(request.get_json())
            result = AuthService.verify_otp(
                email=data['email'],
                otp=data['otp'],
                role=data.get('role')
            )
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 401

@auth_ns.route('/me')
class Me(Resource):
    @auth_ns.doc('get_current_user')
    @auth_ns.marshal_with(user_response_model)
    @jwt_required()
    def get(self):
        """Get current user"""
        try:
            user = AuthService.get_current_user()
            return user, 200
        except Exception as e:
            return {'message': str(e)}, 500

@auth_ns.route('/config/signup')
class SignupConfigResource(Resource):
    @auth_ns.doc('get_signup_config')
    @auth_ns.marshal_with(signup_config_model)
    def get(self):
        """Get signup configuration"""
        try:
            from models import SystemConfig
            config = SystemConfig.query.get('signup_enabled')
            return {'enabled': config.value.lower() == 'true' if config else True}, 200
        except Exception as e:
            return {'message': str(e)}, 500

    @auth_ns.doc('update_signup_config')
    @auth_ns.expect(signup_config_model)
    @auth_ns.marshal_with(signup_config_model)
    @jwt_required()
    def post(self):
        """Update signup configuration (Admin only)"""
        try:
            user = AuthService.get_current_user()
            if not user.is_admin():
                return {"message": "Admin access required"}, 403
            
            data = request.get_json()
            enabled = data.get('enabled', True)
            
            from models import SystemConfig, db
            config = SystemConfig.query.get('signup_enabled')
            if not config:
                config = SystemConfig(key='signup_enabled', description='Enable or disable public user registration')
                db.session.add(config)
            
            config.value = str(enabled).lower()
            db.session.commit()
            
            return {'enabled': config.value == 'true', 'message': 'Configuration updated'}, 200
        except Exception as e:
            return {'message': str(e)}, 500
