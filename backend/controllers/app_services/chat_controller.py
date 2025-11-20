from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from services import ChatService, GuardrailsService

# Create blueprint
chat_bp = SmoreBlueprint(
    'chat',
    __name__,
    url_prefix='/api/chat',
    description='LangGraph tool calling chat endpoints'
)

# Schemas
from dtos.app_data.chat_dto import (
    ToolChatRequestSchema, ToolChatResponseSchema, ChatHistorySchema
)

# Routes
@chat_bp.route('/tool-calling')
class ToolChatView(MethodView):
    @jwt_required()
    @chat_bp.arguments(ToolChatRequestSchema)
    @chat_bp.response(200, ToolChatResponseSchema)
    def post(self, data):
        """Chat with tool calling"""
        try:
            user_id = get_jwt_identity()
            
            # Check guardrails on input
            guardrails_result = GuardrailsService.check_content(
                data['message'],
                user_id,
                'input'
            )
            
            if not guardrails_result['passed']:
                abort(400, message='Content violates guardrails',
                      violations=guardrails_result['violations'])
            
            # Initialize chat service
            chat_service = ChatService()
            
            # Get recent chat history
            history = chat_service.get_chat_history(user_id, 'tool', limit=10)
            
            # Process chat
            response = chat_service.chat_with_tools(
                message=data['message'],
                user_id=user_id,
                chat_history=history
            )
            
            # Check guardrails on output
            output_check = GuardrailsService.check_content(
                response['answer'],
                user_id,
                'output'
            )
            
            if not output_check['passed']:
                response['answer'] = output_check['cleaned_content']
            
            return response
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'Chat failed: {str(e)}')

@chat_bp.route('/history')
class ChatHistoryView(MethodView):
    @jwt_required()
    @chat_bp.response(200, ChatHistorySchema(many=True))
    def get(self):
        """Get chat history"""
        try:
            user_id = get_jwt_identity()
            chat_service = ChatService()
            history = chat_service.get_chat_history(user_id, limit=50)
            return history
        except Exception as e:
            abort(500, message=str(e))
    
    @jwt_required()
    def delete(self):
        """Clear chat history"""
        try:
            user_id = get_jwt_identity()
            chat_service = ChatService()
            result = chat_service.clear_chat_history(user_id)
            return result
        except Exception as e:
            abort(500, message=str(e))
