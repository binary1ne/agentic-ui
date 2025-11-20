from marshmallow import Schema, fields

class DocumentSchema(Schema):
    """Document schema"""
    id = fields.Int()
    filename = fields.Str()
    user_id = fields.Int()
    uploaded_at = fields.Str()
    file_size = fields.Int(allow_none=True)

class RagChatRequestSchema(Schema):
    """RAG chat request schema"""
    query = fields.Str(required=True)
    use_internet = fields.Bool(missing=False)

class SourceSchema(Schema):
    """Source schema"""
    content = fields.Str()
    metadata = fields.Dict()

class RagChatResponseSchema(Schema):
    """RAG chat response schema"""
    answer = fields.Str()
    sources = fields.List(fields.Nested(SourceSchema))
    use_internet = fields.Bool()
