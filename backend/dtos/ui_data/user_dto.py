from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """User schema"""
    id = fields.Int()
    email = fields.Email()
    full_name = fields.Str(allow_none=True)
    roles = fields.List(fields.Str())  # Updated for RBAC
    created_at = fields.Str()

class CreateUserSchema(Schema):
    """Schema for creating a new user"""
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['user', 'admin']), missing='user')  # Backward compatibility
    roles = fields.List(fields.Str(), missing=None)  # New RBAC field
    full_name = fields.Str(allow_none=True, missing=None)

class UpdateUserSchema(Schema):
    """Schema for updating user details"""
    full_name = fields.Str(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin']))  # Backward compatibility
    roles = fields.List(fields.Str(), allow_none=True)  # New RBAC field
