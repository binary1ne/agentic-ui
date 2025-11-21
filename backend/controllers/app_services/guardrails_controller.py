from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from services.guardrails_services.guardrails_service import GuardrailsService
from services.auth_services.auth_service import AuthService
from dtos.app_data.guardrails_dto import (
    GuardrailConfigSchema, UpdateGuardrailSchema, CreateGuardrailSchema, GuardrailLogSchema
)

from utils.marshmallow_utils import marshmallow_to_restx_model

guardrails_ns = Namespace('guardrails', description='Guardrails management operations')

# Models for Swagger generated from Marshmallow Schemas
guardrail_config_model = marshmallow_to_restx_model(guardrails_ns, GuardrailConfigSchema)
create_guardrail_model = marshmallow_to_restx_model(guardrails_ns, CreateGuardrailSchema)
update_guardrail_model = marshmallow_to_restx_model(guardrails_ns, UpdateGuardrailSchema)
guardrail_log_model = marshmallow_to_restx_model(guardrails_ns, GuardrailLogSchema)

@guardrails_ns.route('/config')
class GuardrailConfigList(Resource):
    @guardrails_ns.doc('get_guardrails_config')
    @guardrails_ns.marshal_list_with(guardrail_config_model)
    @jwt_required()
    def get(self):
        """Get guardrails configuration"""
        try:
            config = GuardrailsService.get_guardrails_config()
            return GuardrailConfigSchema(many=True).dump(config), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @guardrails_ns.doc('create_guardrail_rule')
    @guardrails_ns.expect(create_guardrail_model)
    @guardrails_ns.marshal_with(guardrail_config_model, code=201)
    @jwt_required()
    def post(self):
        """Create new guardrail rule (admin only)"""
        try:
            AuthService.verify_admin()
            data = CreateGuardrailSchema().load(request.get_json())
            rule = GuardrailsService.create_guardrail(**data)
            return GuardrailConfigSchema().dump(rule), 201
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@guardrails_ns.route('/config/<int:rule_id>')
@guardrails_ns.param('rule_id', 'Guardrail Rule ID')
class GuardrailConfig(Resource):
    @guardrails_ns.doc('update_guardrail_rule')
    @guardrails_ns.expect(update_guardrail_model)
    @guardrails_ns.marshal_with(guardrail_config_model)
    @jwt_required()
    def put(self, rule_id):
        """Update guardrail configuration (admin only)"""
        try:
            AuthService.verify_admin()
            data = UpdateGuardrailSchema().load(request.get_json())
            rule = GuardrailsService.update_guardrail(rule_id, **data)
            return GuardrailConfigSchema().dump(rule), 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

    @guardrails_ns.doc('delete_guardrail_rule')
    @jwt_required()
    def delete(self, rule_id):
        """Delete guardrail rule (admin only)"""
        try:
            AuthService.verify_admin()
            result = GuardrailsService.delete_guardrail(rule_id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@guardrails_ns.route('/logs')
class GuardrailLogs(Resource):
    @guardrails_ns.doc('get_guardrails_logs')
    @guardrails_ns.marshal_list_with(guardrail_log_model)
    @jwt_required()
    def get(self):
        """Get guardrails detection logs (admin only)"""
        try:
            AuthService.verify_admin()
            logs = GuardrailsService.get_guardrails_logs(limit=100)
            return GuardrailLogSchema(many=True).dump(logs), 200
        except ValueError as e:
            return {'message': str(e)}, 403
        except Exception as e:
            return {'message': str(e)}, 500
