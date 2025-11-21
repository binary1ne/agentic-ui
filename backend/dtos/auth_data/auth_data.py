from marshmallow import Schema, fields, ValidationError


# Schemas
class SignupSchema(Schema):
    """Signup request schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 6)
    role = fields.Str(missing='user', validate=lambda r: r in ['user', 'admin'])
    full_name = fields.Str(missing=None)

class CheckEmailSchema(Schema):
    """Check email schema"""
    email = fields.Email(required=True)

class LoginSchema(Schema):
    """Login request schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Str(required=False)

class UserResponseSchema(Schema):
    """User response schema"""
    id = fields.Int()
    email = fields.Email()
    full_name = fields.Str(allow_none=True)
    roles = fields.List(fields.Str())
    created_at = fields.Str()

class AuthResponseSchema(Schema):
    """Authentication response schema"""
    user = fields.Nested(UserResponseSchema)
    access_token = fields.Str()

class CheckEmailResponseSchema(Schema):
    """Check email response schema"""
    exists = fields.Bool()
    roles = fields.List(fields.Str())
    full_name = fields.Str()

class SignupConfigSchema(Schema):
    """Signup configuration schema"""
    enabled = fields.Bool(required=True, description='Enable/Disable signup')
