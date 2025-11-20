from marshmallow import Schema, fields, validate

class RoleSchema(Schema):
    """Schema for role data"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    created_at = fields.Str(dump_only=True)


class RoleCreateSchema(Schema):
    """Schema for creating a new role"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))


class RoleUpdateSchema(Schema):
    """Schema for updating a role"""
    name = fields.Str(validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))


class AssignRolesSchema(Schema):
    """Schema for assigning roles to a user"""
    user_id = fields.Int(required=True)
    role_names = fields.List(fields.Str(), required=True)
