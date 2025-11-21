from models import db, UserDetailsModel
from services.auth_services.auth_service import AuthService

class UserService:
    """Service for managing users"""
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        users = UserDetailsModel.query.all()
        return [user.to_dict() for user in users]
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = UserDetailsModel.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        return user.to_dict()
    
    @staticmethod
    def update_user(user_id, data):
        """
        Update user details
        
        Args:
            user_id: User ID
            data: Dict with update data
            
        Returns:
            dict: Updated user data
        """
        user = UserDetailsModel.query.get(user_id)
        if not user:
            raise ValueError('User not found')
            
        if 'full_name' in data:
            user.name = data['full_name']
            
        if 'file_upload_enabled' in data:
            user.file_upload_enabled = data['file_upload_enabled']
            
        if 'two_factor_auth_enabled' in data:
            user.two_factor_auth_enabled = data['two_factor_auth_enabled']
            
        # Handle role updates
        # Support both 'role' (single, legacy) and 'roles' (list, new)
        roles_to_assign = None
        if 'roles' in data and data['roles']:
            roles_to_assign = data['roles']
        elif 'role' in data and data['role']:
            roles_to_assign = [data['role']]
            
        if roles_to_assign:
            AuthService.assign_roles(user.user_id, roles_to_assign)
            
        db.session.commit()
        return user.to_dict()
    
    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        user = UserDetailsModel.query.get(user_id)
        if not user:
            raise ValueError('User not found')
            
        # Prevent deleting last admin
        if user.is_admin():
            admin_count = 0
            all_users = UserDetailsModel.query.all()
            for u in all_users:
                if u.is_admin():
                    admin_count += 1
            
            if admin_count <= 1:
                raise ValueError('Cannot delete the last administrator')
        
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}
