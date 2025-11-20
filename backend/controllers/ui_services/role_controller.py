from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from models import db, Role
from services.auth_service import AuthService
from dtos.role_dto import RoleSchema, RoleCreateSchema, RoleUpdateSchema, AssignRolesSchema

role_bp = Blueprint('roles', __name__, url_prefix='/api/roles', description='Role management')


@role_bp.route('')
class RoleListView(MethodView):
    @jwt_required()
    @role_bp.response(200, RoleSchema(many=True))
    def get(self):
        """Get all roles"""
        try:
            # Allow any authenticated user to view roles
            roles = Role.query.all()
            return [role.to_dict() for role in roles]
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    @role_bp.arguments(RoleCreateSchema)
    @role_bp.response(201, RoleSchema)
    def post(self, data):
        """Create a new role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                abort(403, message="Admin access required")
            
            # Check if role already exists
            if Role.query.filter_by(name=data['name']).first():
                abort(400, message=f"Role '{data['name']}' already exists")
            
            # Create role
            role = Role(
                name=data['name'],
                description=data.get('description')
            )
            db.session.add(role)
            db.session.commit()
            
            return role.to_dict()
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))


@role_bp.route('/<int:role_id>')
class RoleDetailView(MethodView):
    @jwt_required()
    @role_bp.response(200, RoleSchema)
    def get(self, role_id):
        """Get a specific role"""
        try:
            role = Role.query.get(role_id)
            if not role:
                abort(404, message="Role not found")
            return role.to_dict()
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    @role_bp.arguments(RoleUpdateSchema)
    @role_bp.response(200, RoleSchema)
    def put(self, data, role_id):
        """Update a role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                abort(403, message="Admin access required")
            
            role = Role.query.get(role_id)
            if not role:
                abort(404, message="Role not found")
            
            # Prevent modifying default roles
            if role.name in ['admin', 'user']:
                abort(400, message="Cannot modify default system roles")
            
            # Update role
            if 'name' in data:
                # Check if new name conflicts
                existing = Role.query.filter_by(name=data['name']).first()
                if existing and existing.id != role_id:
                    abort(400, message=f"Role '{data['name']}' already exists")
                role.name = data['name']
            
            if 'description' in data:
                role.description = data['description']
            
            db.session.commit()
            return role.to_dict()
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    def delete(self, role_id):
        """Delete a role (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                abort(403, message="Admin access required")
            
            role = Role.query.get(role_id)
            if not role:
                abort(404, message="Role not found")
            
            # Prevent deleting default roles
            if role.name in ['admin', 'user']:
                abort(400, message="Cannot delete default system roles")
            
            # Delete role
            db.session.delete(role)
            db.session.commit()
            
            return {'message': f"Role '{role.name}' deleted successfully"}
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))


@role_bp.route('/assign')
class AssignRolesView(MethodView):
    @jwt_required()
    @role_bp.arguments(AssignRolesSchema)
    def post(self, data):
        """Assign roles to a user (Admin only)"""
        try:
            # Verify admin
            user = AuthService.get_current_user()
            if not user.is_admin():
                abort(403, message="Admin access required")
            
            # Assign roles
            updated_user = AuthService.assign_roles(
                user_id=data['user_id'],
                role_names=data['role_names']
            )
            
            return {'message': 'Roles assigned successfully', 'user': updated_user.to_dict()}
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
