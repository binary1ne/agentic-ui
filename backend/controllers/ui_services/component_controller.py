from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from services import ComponentService, AuthService

# Create blueprint
component_bp = SmoreBlueprint(
    'components',
    __name__,
    url_prefix='/api/components',
    description='Component/View management endpoints'
)

# Schemas
from dtos.ui_data.component_dto import (
    ComponentsListSchema, AssignComponentSchema, ComponentAccessSchema,
    ComponentListResponseSchema, NavigationItemSchema, NavigationResponseSchema
)

# Routes
@component_bp.route('')
class ComponentsListView(MethodView):
    @component_bp.response(200, ComponentsListSchema)
    def get(self):
        """Get available components"""
        try:
            components = ComponentService.get_available_components()
            return components
        except Exception as e:
            abort(500, message=str(e))

@component_bp.route('/user')
class UserComponentsView(MethodView):
    @jwt_required()
    @component_bp.response(200, ComponentListResponseSchema)
    def get(self):
        """Get current user's accessible components"""
        try:
            components = ComponentService.get_user_components()
            return {'components': components}
        except Exception as e:
            abort(500, message=str(e))

@component_bp.route('/assign')
class AssignComponentView(MethodView):
    @jwt_required()
    @component_bp.arguments(AssignComponentSchema)
    @component_bp.response(200, ComponentAccessSchema)
    def post(self, data):
        """Assign component to role (admin only)"""
        try:
            AuthService.verify_admin()
            result = ComponentService.assign_component_to_role(
                role=data['role'],
                component_name=data['component_name'],
                has_access=data.get('has_access', True)
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))

@component_bp.route('/role/<string:role>')
class RoleComponentsView(MethodView):
    @jwt_required()
    @component_bp.response(200, ComponentListResponseSchema)
    def get(self, role):
        """Get components for a specific role (admin only)"""
        try:
            AuthService.verify_admin()
            components = ComponentService.get_role_components(role)
            return {'components': components}
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))

@component_bp.route('/navigation')
class NavigationListView(MethodView):
    @jwt_required()
    @component_bp.response(200, NavigationResponseSchema)
    def get(self):
        """Get navigation menu for current user"""
        try:
            nav_items = ComponentService.get_navigation_for_user()
            return {'navigation': nav_items}
        except Exception as e:
            abort(500, message=str(e))
