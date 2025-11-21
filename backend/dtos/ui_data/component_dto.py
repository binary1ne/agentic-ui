from marshmallow import Schema, fields

class ComponentsListSchema(Schema):
    """Components list schema"""
    assignable = fields.List(fields.Str())
    admin_only = fields.List(fields.Str())

class AssignComponentSchema(Schema):
    """Assign component schema"""
    role = fields.Str(required=True)
    component_name = fields.Str(required=True)
    has_access = fields.Bool(missing=True)

class ComponentAccessSchema(Schema):
    """Component access schema"""
    id = fields.Int(attribute='template_role_id')
    role = fields.Str(attribute='role_name')
    component_name = fields.Str(attribute='template_name')
    has_access = fields.Bool(attribute='active_flag')

class ComponentListResponseSchema(Schema):
    """Component list response schema"""
    components = fields.List(fields.Str())

class NavigationItemSchema(Schema):
    """Navigation item schema"""
    name = fields.Str()
    label = fields.Str()
    icon = fields.Str()
    description = fields.Str(allow_none=True)
    admin_only = fields.Bool()
    mode = fields.Str(allow_none=True)
    value = fields.Str(allow_none=True)

class NavigationResponseSchema(Schema):
    """Navigation response schema"""
    navigation = fields.List(fields.Nested(NavigationItemSchema))
