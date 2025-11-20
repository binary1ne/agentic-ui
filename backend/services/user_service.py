from models import db, User, Role
from services.auth_service import AuthService

class UserService:
    """User management service"""
    
    @staticmethod
    def get_all_users():
        """
        Get all users (admin only)
        
        Returns:
            list: List of all users
        """
        users = User.query.all()
        return [user.to_dict() for user in users]
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User data
            
        Raises:
            ValueError: If user not found
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('User not found')
        
        return user.to_dict()
    
    @staticmethod
    def update_user_roles(user_id, role_names):
        """
        Update user roles (admin only)
        
        Args:
            user_id: User ID
            role_names: List of role names to assign
            
        Returns:
            dict: Updated user data
            
        Raises:
            ValueError: If user not found or invalid role
        """
        return AuthService.assign_roles(user_id, role_names).to_dict()
    
    @staticmethod
    def update_user(user_id, data):
        """
        Update user details (admin only)
        
        Args:
            user_id: User ID
            data: Dictionary of fields to update
            
        Returns:
            dict: Updated user data
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('User not found')
            
        if 'full_name' in data:
            user.full_name = data['full_name']
            
        if 'roles' in data:
            # Update roles using AuthService
            AuthService.assign_roles(user_id, data['roles'])
        elif 'role' in data:
            # Backwards compatibility: single role
            AuthService.assign_roles(user_id, [data['role']])
                
        db.session.commit()
        return user.to_dict()
    
    @staticmethod
    def delete_user(user_id):
        """
        Delete user (admin only)
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Success message
            
        Raises:
            ValueError: If user not found or trying to delete self
        """
        current_user = AuthService.get_current_user()
        
        if current_user.id == user_id:
            raise ValueError('Cannot delete your own account')
        
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('User not found')
        
        db.session.delete(user)
        db.session.commit()
        
        return {'message': f'User {user.email} deleted successfully'}
    
    @staticmethod
    def create_user(email, password, role='user', full_name=None):
        """
        Create a new user (admin only)
        
        Args:
            email: User email
            password: User password
            role: User role (can be single role or list)
            full_name: User's full name
            
        Returns:
            dict: Created user data
        """
        # Convert single role to list
        roles = [role] if isinstance(role, str) else role
        
        # Use AuthService to create user
        user = AuthService.create_user(
            email=email,
            password=password,
            roles=roles,
            full_name=full_name
        )
        
        return user.to_dict()
