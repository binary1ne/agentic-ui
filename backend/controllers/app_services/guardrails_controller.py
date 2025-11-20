from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from services import GuardrailsService, AuthService

# Create blueprint
guardrails_bp = SmoreBlueprint(
    'guardrails',
    __name__,
    url_prefix='/api/guardrails',
    description='Guardrails configuration and logs endpoints'
)

# Schemas
from dtos.app_data.guardrails_dto import (
    GuardrailConfigSchema, UpdateGuardrailSchema, CreateGuardrailSchema, GuardrailLogSchema
)

# Routes
@guardrails_bp.route('/config')
class GuardrailsConfigView(MethodView):
    @jwt_required()
    @guardrails_bp.response(200, GuardrailConfigSchema(many=True))
    def get(self):
        """Get guardrails configuration"""
        try:
            config = GuardrailsService.get_guardrails_config()
            return config
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    @guardrails_bp.arguments(CreateGuardrailSchema)
    @guardrails_bp.response(201, GuardrailConfigSchema)
    def post(self, data):
        """Create new guardrail rule (admin only)"""
        try:
            AuthService.verify_admin()
            rule = GuardrailsService.create_guardrail(**data)
            return rule
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))

@guardrails_bp.route('/config/<int:rule_id>')
class GuardrailConfigView(MethodView):
    @jwt_required()
    @guardrails_bp.arguments(UpdateGuardrailSchema)
    @guardrails_bp.response(200, GuardrailConfigSchema)
    def put(self, data, rule_id):
        """Update guardrail configuration (admin only)"""
        try:
            AuthService.verify_admin()
            rule = GuardrailsService.update_guardrail(rule_id, **data)
            return rule
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    def delete(self, rule_id):
        """Delete guardrail rule (admin only)"""
        try:
            AuthService.verify_admin()
            result = GuardrailsService.delete_guardrail(rule_id)
            return result
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=str(e))

@guardrails_bp.route('/logs')
class GuardrailsLogsView(MethodView):
    @jwt_required()
    @guardrails_bp.response(200, GuardrailLogSchema(many=True))
    def get(self):
        """Get guardrails detection logs (admin only)"""
        try:
            AuthService.verify_admin()
            logs = GuardrailsService.get_guardrails_logs(limit=100)
            return logs
        except ValueError as e:
            abort(403, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
