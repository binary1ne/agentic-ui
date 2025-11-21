from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """User schema"""
    id = fields.Int(attribute='user_id')
    email = fields.Email()
    full_name = fields.Str(attribute='name', allow_none=True)
    roles = fields.Method("get_roles")
    file_upload_enabled = fields.Bool()
    two_factor_auth_enabled = fields.Bool()
    created_at = fields.Str()

    def get_roles(self, obj):
        if hasattr(obj, 'get_role_names'):
            return obj.get_role_names()
        return []

class CreateUserSchema(Schema):
    """Schema for creating a new user"""
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['user', 'admin']), missing='user')  # Backward compatibility
    roles = fields.List(fields.Str(), missing=None)  # New RBAC field
    full_name = fields.Str(allow_none=True, missing=None)
    file_upload_enabled = fields.Bool(missing=False)
    two_factor_auth_enabled = fields.Bool(missing=False)

class UpdateUserSchema(Schema):
    """Schema for updating user details"""
    full_name = fields.Str(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin']))  # Backward compatibility
    roles = fields.List(fields.Str(), allow_none=True)  # New RBAC field
    file_upload_enabled = fields.Bool(allow_none=True)
    two_factor_auth_enabled = fields.Bool(allow_none=True)
