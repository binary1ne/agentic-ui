from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from services.system_services.user_service import UserService
from services.auth_services.auth_service import AuthService
from dtos.ui_data.user_dto import (
    UserSchema, CreateUserSchema, UpdateUserSchema
)

from utils.marshmallow_utils import marshmallow_to_restx_model

user_ns = Namespace('users', description='User management operations')

# Models for Swagger generated from Marshmallow Schemas
user_model = marshmallow_to_restx_model(user_ns, UserSchema)
create_user_model = marshmallow_to_restx_model(user_ns, CreateUserSchema)
update_user_model = marshmallow_to_restx_model(user_ns, UpdateUserSchema)

@user_ns.route('')
class UserList(Resource):
    @user_ns.doc('list_users')
    @user_ns.marshal_list_with(user_model)
    @jwt_required()
    def get(self):
        """List all users (admin only)"""
        try:
            AuthService.verify_admin()
            users = UserService.get_all_users()
            # We can return objects directly if they match the model, 
            # but since we have UserSchema, we might want to use it or let marshal_with handle it.
            # marshal_with expects objects or dicts. 
            # UserService.get_all_users() returns model instances.
            return users, 200
        except ValueError as e:
            user_ns.abort(403, str(e))
        except Exception as e:
            user_ns.abort(500, str(e))

    @user_ns.doc('create_user')
    @user_ns.expect(create_user_model)
    @user_ns.marshal_with(user_model, code=201)
    @jwt_required()
    def post(self):
        """Create new user (admin only)"""
        try:
            AuthService.verify_admin()
            data = CreateUserSchema().load(request.get_json())
            
            # Handle both old 'role' and new 'roles' parameter
            roles_to_assign = data.get('roles') or [data.get('role', 'user')]
            
            user = AuthService.create_user(
                email=data['email'],
                password=data['password'],
                roles=roles_to_assign,
                full_name=data.get('full_name'),
                file_upload_enabled=data.get('file_upload_enabled', False),
                two_factor_auth_enabled=data.get('two_factor_auth_enabled', False)
            )
            return user, 201
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@user_ns.route('/<int:user_id>')
@user_ns.param('user_id', 'The user identifier')
@user_ns.response(404, 'User not found')
class User(Resource):
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def get(self, user_id):
        """Get user by ID (admin only)"""
        try:
            AuthService.verify_admin()
            user = UserService.get_user_by_id(user_id)
            return user, 200
        except ValueError as e:
            return {'message': str(e)}, 404
        except Exception as e:
            return {'message': str(e)}, 500

    @user_ns.doc('update_user')
    @user_ns.expect(update_user_model)
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def put(self, user_id):
        """Update user details (admin only)"""
        try:
            AuthService.verify_admin()
            data = UpdateUserSchema().load(request.get_json())
            user = UserService.update_user(user_id, data)
            return user, 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

    @user_ns.doc('delete_user')
    @jwt_required()
    def delete(self, user_id):
        """Delete user (admin only)"""
        try:
            AuthService.verify_admin()
            result = UserService.delete_user(user_id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
