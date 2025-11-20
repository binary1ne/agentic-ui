from marshmallow import Schema, fields

class GuardrailConfigSchema(Schema):
    """Guardrail config schema"""
    id = fields.Int()
    rule_type = fields.Str()
    enabled = fields.Bool()
    severity = fields.Str()
    description = fields.Str()
    pattern = fields.Str()

class UpdateGuardrailSchema(Schema):
    """Update guardrail schema"""
    enabled = fields.Bool()
    severity = fields.Str()
    description = fields.Str()
    pattern = fields.Str()

class CreateGuardrailSchema(Schema):
    """Create guardrail schema"""
    rule_type = fields.Str(required=True)
    enabled = fields.Bool(missing=True)
    severity = fields.Str(missing='medium')
    description = fields.Str()
    pattern = fields.Str()

class GuardrailLogSchema(Schema):
    """Guardrail log schema"""
    id = fields.Int()
    user_id = fields.Int()
    user_email = fields.Str()
    detected_rule = fields.Str()
    content_snippet = fields.Str()
    timestamp = fields.Str()
    action_taken = fields.Str()
