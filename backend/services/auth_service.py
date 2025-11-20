from flask_jwt_extended import create_access_token, get_jwt_identity
from models import db, User, Role
from datetime import timedelta

class AuthService:
    """Authentication service for user registration and login"""
    
    @staticmethod
    def create_user(email, password, roles=None, full_name=None):
        """
        Create a new user
        
        Args:
            email: User email
            password: User password
            roles: List of role names (default: ['user'])
            full_name: User's full name
            
        Returns:
            User: Created user object
            
        Raises:
            ValueError: If email already exists or invalid data
        """
        # Validate email
        if not email or '@' not in email:
            raise ValueError('Invalid email address')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
        
        # Validate password
        if not password or len(password) < 6:
            raise ValueError('Password must be at least 6 characters')
        
        # Default to 'user' role if not specified
        if roles is None:
            roles = ['user']
        
        # Create user
        user = User(email=email, full_name=full_name)
        user.set_password(password)
        
        # Assign roles
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f'Role not found: {role_name}')
            user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        return user

    @staticmethod
    def register_user(email, password, role='user', full_name=None):
        """Register a new user (alias for create_user with token generation)"""
        # Convert single role to list for compatibility
        roles = [role] if isinstance(role, str) else role
        user = AuthService.create_user(email, password, roles, full_name)
        
        # Generate JWT token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'roles': user.get_role_names()}
        )
        
        return {
            'user': user.to_dict(),
            'access_token': access_token
        }
    
    @staticmethod
    def check_user_exists(email):
        """
        Check if user exists and return roles
        
        Args:
            email: User email
            
        Returns:
            dict: User existence and roles
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return {'exists': False}
            
        return {
            'exists': True,
            'roles': user.get_role_names(),
            'full_name': user.full_name
        }

    @staticmethod
    def login_user(email, password, role=None):
        """
        Login user and generate JWT token
        
        Args:
            email: User email
            password: User password
            role: Optional role to validate against (deprecated, kept for compatibility)
            
        Returns:
            dict: User data and access token
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError('Invalid credentials')
        
        # Verify password
        if not user.check_password(password):
            raise ValueError('Invalid credentials')
            
        # Verify role if provided (for backwards compatibility)
        if role and not user.has_role(role):
            raise ValueError(f'User does not have {role} access')
        
        # Generate JWT token with roles
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'roles': user.get_role_names()}
        )
        
        return {
            'user': user.to_dict(),
            'access_token': access_token
        }
    
    @staticmethod
    def get_current_user():
        """
        Get current authenticated user
        
        Returns:
            User: Current user object
            
        Raises:
            ValueError: If user not found
        """
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            raise ValueError('User not found')
        
        return user
    
    @staticmethod
    def verify_admin():
        """
        Verify current user is admin
        
        Returns:
            User: Current user if admin
            
        Raises:
            ValueError: If user is not admin
        """
        user = AuthService.get_current_user()
        
        if not user.is_admin():
            raise ValueError('Admin access required')
        
        return user
    
    @staticmethod
    def assign_roles(user_id, role_names):
        """
        Assign roles to a user
        
        Args:
            user_id: User ID
            role_names: List of role names to assign
            
        Returns:
            User: Updated user object
            
        Raises:
            ValueError: If user or role not found
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        # Clear existing roles
        user.roles = []
        
        # Assign new roles
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f'Role not found: {role_name}')
            user.roles.append(role)
        
        db.session.commit()
        return user
