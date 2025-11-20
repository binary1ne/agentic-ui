from marshmallow import Schema, fields

class ToolChatRequestSchema(Schema):
    """Tool chat request schema"""
    message = fields.Str(required=True)

class ToolResultSchema(Schema):
    """Tool result schema"""
    tool = fields.Str()
    input = fields.Str()
    result = fields.Str()

class ToolChatResponseSchema(Schema):
    """Tool chat response schema"""
    answer = fields.Str()
    tools_used = fields.List(fields.Str())
    tool_results = fields.List(fields.Nested(ToolResultSchema))

class ChatHistorySchema(Schema):
    """Chat history schema"""
    id = fields.Int()
    user_id = fields.Int()
    message = fields.Str()
    response = fields.Str()
    chat_type = fields.Str()
    timestamp = fields.Str()
    metadata = fields.Dict()
