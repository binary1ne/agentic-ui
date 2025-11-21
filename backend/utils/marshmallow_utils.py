from flask_restx import fields as restx_fields
from marshmallow import fields as ma_fields
from marshmallow import Schema

def marshmallow_to_restx_model(api, schema_cls, model_name=None):
    """
    Convert a Marshmallow Schema class to a Flask-RestX Model.
    
    Args:
        api: The Flask-RestX Api or Namespace instance.
        schema_cls: The Marshmallow Schema class.
        model_name: Optional name for the model. If None, uses schema class name.
        
    Returns:
        A Flask-RestX Model.
    """
    if not model_name:
        model_name = schema_cls.__name__.replace('Schema', '')
        
    model_fields = {}
    
    # Instantiate schema to get fields
    schema = schema_cls()
    
    for field_name, field in schema.fields.items():
        restx_field = _convert_field(field, api)
        if restx_field:
            model_fields[field_name] = restx_field
            
    return api.model(model_name, model_fields)

def _convert_field(field, api):
    """Helper to convert a single Marshmallow field to RestX field."""
    if isinstance(field, ma_fields.Nested):
        # Handle nested schemas
        nested_schema = field.nested
        if isinstance(nested_schema, str):
            # Handle string reference if needed, but usually it's a class or instance
            # For simplicity, assume it's a class or instance we can inspect
            # This might be complex if it's a string 'Self' etc.
            return restx_fields.Raw() 
        
        if isinstance(nested_schema, type) and issubclass(nested_schema, Schema):
            nested_model = marshmallow_to_restx_model(api, nested_schema)
        elif isinstance(nested_schema, Schema):
            nested_model = marshmallow_to_restx_model(api, type(nested_schema))
        else:
            return restx_fields.Raw()
            
        if field.many:
            return restx_fields.List(restx_fields.Nested(nested_model))
        else:
            return restx_fields.Nested(nested_model)
            
    if isinstance(field, ma_fields.List):
        inner_field = _convert_field(field.inner, api)
        if inner_field:
            return restx_fields.List(inner_field)
        return restx_fields.List(restx_fields.String)
        
    if isinstance(field, ma_fields.Integer):
        return restx_fields.Integer(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Boolean):
        return restx_fields.Boolean(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Float):
        return restx_fields.Float(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Number):
        return restx_fields.Float(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Date):
        return restx_fields.Date(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.DateTime):
        return restx_fields.DateTime(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.String):
        return restx_fields.String(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Dict):
        return restx_fields.Raw(description=field.metadata.get('description'), required=field.required)
    if isinstance(field, ma_fields.Raw):
        return restx_fields.Raw(description=field.metadata.get('description'), required=field.required)
        
    # Default to String for unknown types
    return restx_fields.String(description=field.metadata.get('description'), required=field.required)
