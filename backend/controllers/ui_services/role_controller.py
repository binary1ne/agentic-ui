from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from models import db
from models import RoleModel
from services.auth_services.auth_service import AuthService
from dtos.role_dto import RoleSchema, RoleCreateSchema, RoleUpdateSchema, AssignRolesSchema

from utils.marshmallow_utils import marshmallow_to_restx_model

role_ns = Namespace('roles', description='Role management operations')

# Models for Swagger generated from Marshmallow Schemas
role_model = marshmallow_to_restx_model(role_ns, RoleSchema)
create_role_model = marshmallow_to_restx_model(role_ns, RoleCreateSchema)
update_role_model = marshmallow_to_restx_model(role_ns, RoleUpdateSchema)
assign_roles_model = marshmallow_to_restx_model(role_ns, AssignRolesSchema)

@role_ns.route('')
class RoleList(Resource):
    @role_ns.doc('list_roles')
    @jwt_required()
    def get(self):
        """Get all roles"""
        try:
            # Allow any authenticated user to view roles
            roles = RoleModel.query.all()
            # Manually serialize using Marshmallow to ensure attribute mapping works
            schema = RoleSchema(many=True)
            return schema.dump(roles), 200
        except Exception as e:
            role_ns.abort(500, str(e))

    @role_ns.doc('create_role')
    @role_ns.expect(create_role_model)
    @jwt_required()
    def post(self):
        """Create a new role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                role_ns.abort(403, "Admin access required")
            
            data = RoleCreateSchema().load(request.get_json())
            
            # Check if role already exists
            if RoleModel.query.filter_by(role_name=data['name']).first():
                role_ns.abort(400, f"Role '{data['name']}' already exists")
            
            # Create role
            role = RoleModel(
                role_name=data['name'],
                description=data.get('description')
            )
            db.session.add(role)
            db.session.commit()
            
            schema = RoleSchema()
            return schema.dump(role), 201
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@role_ns.route('/<int:role_id>')
@role_ns.param('role_id', 'The role identifier')
@role_ns.response(404, 'Role not found')
class Role(Resource):
    @role_ns.doc('get_role')
    @jwt_required()
    def get(self, role_id):
        """Get a specific role"""
        try:
            role = RoleModel.query.get(role_id)
            if not role:
                role_ns.abort(404, "Role not found")
            schema = RoleSchema()
            return schema.dump(role), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_ns.doc('update_role')
    @role_ns.expect(update_role_model)
    @jwt_required()
    def put(self, role_id):
        """Update a role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                role_ns.abort(403, "Admin access required")
            
            data = RoleUpdateSchema().load(request.get_json())
            
            role = RoleModel.query.get(role_id)
            if not role:
                role_ns.abort(404, "Role not found")
            
            # Prevent modifying default roles
            if role.role_name in ['admin', 'user']:
                role_ns.abort(400, "Cannot modify default system roles")
            
            # Update role
            if 'name' in data:
                # Check if new name conflicts
                existing = RoleModel.query.filter_by(role_name=data['name']).first()
                if existing and existing.role_id != role_id:
                    role_ns.abort(400, f"Role '{data['name']}' already exists")
                role.role_name = data['name']
            
            if 'description' in data:
                role.description = data['description']
            
            db.session.commit()
            schema = RoleSchema()
            return schema.dump(role), 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

    @role_ns.doc('delete_role')
    @jwt_required()
    def delete(self, role_id):
        """Delete a role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                role_ns.abort(403, "Admin access required")
            
            role = RoleModel.query.get(role_id)
            if not role:
                role_ns.abort(404, "Role not found")
            
            # Prevent deleting default roles
            if role.role_name in ['admin', 'user']:
                role_ns.abort(400, "Cannot delete default system roles")
            
            # Delete role
            db.session.delete(role)
            db.session.commit()
            
            return {'message': f"Role '{role.role_name}' deleted successfully"}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@role_ns.route('/assign')
class RoleAssignment(Resource):
    @role_ns.doc('assign_roles')
    @role_ns.expect(assign_roles_model)
    @jwt_required()
    def post(self):
        """Assign roles to a user (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                role_ns.abort(403, "Admin access required")
            
            data = AssignRolesSchema().load(request.get_json())
            
            AuthService.assign_roles(
                user_id=data['user_id'],
                role_names=data['role_names']
            )
            
            return {'message': 'Roles assigned successfully'}, 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
