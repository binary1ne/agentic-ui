from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

from services.ui_services.component_service import ComponentService
from services.auth_services.auth_service import AuthService
from dtos.ui_data.component_dto import (
    ComponentsListSchema, AssignComponentSchema, ComponentAccessSchema,
    ComponentListResponseSchema, NavigationResponseSchema
)

from utils.marshmallow_utils import marshmallow_to_restx_model

component_ns = Namespace('components', description='Component management operations')

# Models for Swagger generated from Marshmallow Schemas
component_list_model = marshmallow_to_restx_model(component_ns, ComponentsListSchema)
assign_component_model = marshmallow_to_restx_model(component_ns, AssignComponentSchema)
component_access_model = marshmallow_to_restx_model(component_ns, ComponentAccessSchema)
component_response_model = marshmallow_to_restx_model(component_ns, ComponentListResponseSchema)
navigation_model = marshmallow_to_restx_model(component_ns, NavigationResponseSchema)
# NavigationItemSchema is nested in NavigationResponseSchema, so it will be handled automatically

@component_ns.route('')
class ComponentList(Resource):
    @component_ns.doc('list_components')
    # @component_ns.marshal_with(component_list_model) # ComponentsListSchema
    @jwt_required()
    def get(self):
        """Get available components"""
        try:
            components = ComponentService.get_available_components()
            return components, 200
        except Exception as e:
            return {'message': str(e)}, 500

@component_ns.route('/user')
class UserComponents(Resource):
    @component_ns.doc('get_user_components')
    @component_ns.marshal_with(component_response_model)
    @jwt_required()
    def get(self):
        """Get current user's accessible components"""
        try:
            components = ComponentService.get_user_components()
            return {'components': components}, 200
        except Exception as e:
            return {'message': str(e)}, 500

@component_ns.route('/assign')
class AssignComponent(Resource):
    @component_ns.doc('assign_component')
    @component_ns.expect(assign_component_model)
    @component_ns.marshal_with(component_access_model)
    @jwt_required()
    def post(self):
        """Assign component to role (admin only)"""
        try:
            AuthService.verify_admin()
            data = AssignComponentSchema().load(request.get_json())
            result = ComponentService.assign_component_to_role(
                role_name=data['role'],
                component_name=data['component_name'],
                has_access=data.get('has_access', True)
            )
            return result, 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@component_ns.route('/role/<string:role>')
@component_ns.param('role', 'Role name')
class RoleComponents(Resource):
    @component_ns.doc('get_role_components')
    @component_ns.marshal_with(component_response_model)
    @jwt_required()
    def get(self, role):
        """Get components for a specific role (admin only)"""
        try:
            AuthService.verify_admin()
            components = ComponentService.get_role_components(role)
            return {'components': components}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@component_ns.route('/navigation')
class Navigation(Resource):
    @component_ns.doc('get_navigation')
    @jwt_required()
    def get(self):
        """Get navigation menu for current user based on ACTIVE ROLE from JWT"""
        try:
            # Extract claims from JWT logic
            claims = get_jwt()
            active_role = claims.get('role')

            if not active_role:
                return {'error': 'No active role found in JWT'}, 400

            nav_items = ComponentService.get_navigation(active_role)
            return {'navigation': nav_items}, 200

        except Exception as e:
            return {'message': str(e), 'error': 'Failed to load navigation'}, 500
