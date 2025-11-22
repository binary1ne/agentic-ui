from datetime import datetime, timedelta
import random
import string
from flask_jwt_extended import create_access_token

from .email_service import EmailService
from config import Config
from models import db
from models import UserDetailsModel, RoleModel, UserRoleMappingModel

from .otp_store import OTPStore

class AuthService:
    """Authentication and Authorization Service"""
    
    @staticmethod
    def login_user(email, password, role=None):
        print("Login User",email,password,role)
        """
        Authenticate user and return token or 2FA requirement
        
        Args:
            email: User email
            password: User password
            role: Optional specific role to login as
            
        Returns:
            dict: Auth response
        """
        user = UserDetailsModel.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            raise ValueError('Invalid email or password')
            
        if not user.active_flag:
            raise ValueError('User account is inactive')
            
        # Check if 2FA is enabled
        if user.two_factor_auth_enabled:
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Store OTP in memory
            OTPStore().store_otp(user.email, otp, ttl_seconds=600)
            
            # Send email
            EmailService.send_otp_email(user.email, otp)
            
            return {
                'requires_2fa': True,
                'message': 'OTP sent to your email',
                'email': email # Return email to help frontend context
            }
            
        # If no 2FA, proceed to generate token
        return AuthService._generate_token_response(user, role)

    @staticmethod
    def verify_otp(email, otp, role=None):
        """
        Verify OTP and return token
        """
        user = UserDetailsModel.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError('User not found')
            
        # Verify OTP from memory store
        if not OTPStore().verify_otp(email, otp):
            raise ValueError('Invalid or expired OTP')
        
        return AuthService._generate_token_response(user, role)

    @staticmethod
    def _generate_token_response(user, role=None):
        """Generate JWT token response"""
        # Get user roles
        print("User Roles",user.get_role_names())
        user_roles = user.get_role_names()
        
        if not user_roles:
            raise ValueError('User has no assigned roles')
            
        # If role requested, verify user has it
        if role:
            if role not in user_roles:
                raise ValueError(f'User does not have role: {role}')
            active_role = role
        else:
            # Default to first role (prefer admin if available)
            active_role = 'admin' if 'admin' in user_roles else user_roles[0]
            
        # Create access token
        print("Generating JWT Token",user.user_id,active_role,user_roles,user.email,user.name)
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={
                'role': active_role,
                'roles': user_roles,
                'email': user.email,
                'name': user.name
            }
        )
        
        return {
            'access_token': access_token,
            'user': user.to_dict(),
            'role': active_role,
            'requires_2fa': False
        }
    
    @staticmethod
    def create_user(email, password, roles=None, full_name=None, file_upload_enabled=False, two_factor_auth_enabled=False):
        """
        Create new user
        """
        if UserDetailsModel.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
            
        user = UserDetailsModel(
            email=email, 
            name=full_name,
            file_upload_enabled=file_upload_enabled,
            two_factor_auth_enabled=two_factor_auth_enabled
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # Get ID
        
        # Assign roles
        if roles:
            AuthService.assign_roles(user.user_id, roles)
        else:
            # Default role
            AuthService.assign_roles(user.user_id, ['user'])
            
        db.session.commit()
        return user
    
    @staticmethod
    def register_user(email, password, role='user', full_name=None):
        """Register a new user (public signup)"""
        # Check if signup is enabled is handled in controller
        return AuthService.create_user(email, password, [role], full_name)

    @staticmethod
    def assign_roles(user_id, role_names):
        """Assign roles to user"""
        user = UserDetailsModel.query.get(user_id)
        if not user:
            raise ValueError('User not found')
            
        # Deactivate existing roles
        for user_role in user.user_roles:
            user_role.active_flag = False
            
        # Add new roles
        for role_name in role_names:
            role = RoleModel.query.filter_by(role_name=role_name).first()
            if not role:
                continue
                
            # Check if mapping exists
            mapping = UserRoleMappingModel.query.filter_by(
                user_id=user.user_id,
                role_id=role.role_id
            ).first()
            
            if mapping:
                mapping.active_flag = True
            else:
                mapping = UserRoleMappingModel(
                    user_id=user.user_id,
                    role_id=role.role_id,
                    active_flag=True
                )
                db.session.add(mapping)
                
        db.session.commit()

    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        return UserDetailsModel.query.get(user_id)

    @staticmethod
    def verify_admin():
        """Verify current user is admin"""
        user = AuthService.get_current_user()
        if not user or not user.is_admin():
            raise ValueError('Admin access required')
        return user
        
    @staticmethod
    def check_user_exists(email):
        """Check if user exists and return their roles"""
        user = UserDetailsModel.query.filter_by(email=email).first()
        if user:
            return {
                'exists': True,
                'roles': user.get_role_names()  # Return all roles, not just first
            }
        return {'exists': False, 'roles': []}
