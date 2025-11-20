from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from services import UserService, AuthService

# Create blueprint
user_bp = SmoreBlueprint(
    'users',
    __name__,
    url_prefix='/api/users',
    description='User management endpoints (admin only)'
)

# Schemas
from dtos.ui_data.user_dto import (
    UserSchema, CreateUserSchema, UpdateUserSchema
)

# Routes
@user_bp.route('')
class UsersListView(MethodView):
    @jwt_required()
    @user_bp.response(200, UserSchema(many=True))
    def get(self):
        """List all users (admin only)"""
        try:
            AuthService.verify_admin()
            users = UserService.get_all_users()
            return users
        except ValueError as e:
            abort(403, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    @user_bp.arguments(CreateUserSchema)
    @user_bp.response(201, UserSchema)
    def post(self, data):
        """Create new user (admin only)"""
        try:
            AuthService.verify_admin()
            
            # Handle both old 'role' and new 'roles' parameter
            roles_to_assign = data.get('roles') or [data.get('role', 'user')]
            
            user = AuthService.create_user(
                email=data['email'],
                password=data['password'],
                roles=roles_to_assign,
                full_name=data.get('full_name')
            )
            return user.to_dict()
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))

@user_bp.route('/<int:user_id>')
class UserView(MethodView):
    @jwt_required()
    @user_bp.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID (admin only)"""
        try:
            AuthService.verify_admin()
            user = UserService.get_user_by_id(user_id)
            return user
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
            
    @jwt_required()
    @user_bp.arguments(UpdateUserSchema)
    @user_bp.response(200, UserSchema)
    def put(self, data, user_id):
        """Update user details (admin only)"""
        try:
            AuthService.verify_admin()
            user = UserService.update_user(user_id, data)
            return user
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    def delete(self, user_id):
        """Delete user (admin only)"""
        try:
            AuthService.verify_admin()
            result = UserService.delete_user(user_id)
            return result
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
