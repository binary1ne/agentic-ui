import os
import uuid
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from services.agentic_services.chat_service import ChatService
from services.guardrails_services.guardrails_service import GuardrailsService
from dtos.app_data.chat_dto import (
    ToolChatRequestSchema, ToolChatResponseSchema, ChatHistorySchema
)
from config import Config

from utils.marshmallow_utils import marshmallow_to_restx_model

chat_ns = Namespace('chat', description='Chat operations with tool calling')

# Models for Swagger generated from Marshmallow Schemas
chat_response_model = marshmallow_to_restx_model(chat_ns, ToolChatResponseSchema)
chat_history_model = marshmallow_to_restx_model(chat_ns, ChatHistorySchema)
chat_request_model = marshmallow_to_restx_model(chat_ns, ToolChatRequestSchema)

# Parser for multipart/form-data (images + message)
chat_parser = chat_ns.parser()
chat_parser.add_argument('message', type=str, required=True, help='User message', location='form')
# Allow multiple files? reqparse doesn't support multiple files with same key easily in Swagger UI
# But we can define it. For now, let's assume single file or handle manually if needed.
# The original code iterates over request.files, so it supports multiple.
# We can add a few file arguments or just document it.
chat_parser.add_argument('file', type=FileStorage, location='files', help='Optional image file')

# Model for JSON request
chat_request_model = chat_ns.model('ToolChatRequest', {
    'message': fields.String(required=True, description='User message')
})

@chat_ns.route('/tool-calling')
class ToolChat(Resource):
    @chat_ns.doc('tool_chat')
    @chat_ns.expect(chat_parser) # Document multipart first
    # We might need to support JSON as well. Flask-RestX doesn't mix them well in one endpoint doc.
    # But the code handles both.
    @chat_ns.marshal_with(chat_response_model)
    @jwt_required()
    def post(self):
        """Chat with tool calling and optional image support"""
        try:
            user_id = get_jwt_identity()
            
            # Check if request has files (multipart/form-data)
            images = []
            message = None
            
            if request.files or request.form:
                # Handle multipart form data
                message = request.form.get('message')
                if not message:
                    chat_ns.abort(400, 'Message is required')
                
                # Process uploaded images
                for key in request.files:
                    file = request.files[key]
                    if file and file.filename:
                        # Validate image type
                        filename = secure_filename(file.filename)
                        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                        
                        allowed_image_types = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
                        if ext not in allowed_image_types:
                            chat_ns.abort(400, f'Invalid image type. Allowed: {allowed_image_types}')
                        
                        # Save temporarily
                        temp_dir = os.path.join(Config.DOCUMENTS_PATH, 'temp_images')
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        temp_filename = f"{uuid.uuid4()}_{filename}"
                        temp_path = os.path.join(temp_dir, temp_filename)
                        file.save(temp_path)
                        images.append(temp_path)
            else:
                # Handle JSON request
                data = ToolChatRequestSchema().load(request.get_json())
                message = data['message']
            
            # Check guardrails on input
            guardrails_result = GuardrailsService.check_content(
                message,
                user_id,
                'input'
            )
            
            if not guardrails_result['passed']:
                # Clean up temp images
                for img_path in images:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                
                chat_ns.abort(400, 'Content violates guardrails', violations=guardrails_result['violations'])
            
            # Initialize chat service
            chat_service = ChatService()
            
            # Get recent chat history
            history = chat_service.get_chat_history(user_id, 'tool', limit=10)
            
            # Process chat with optional images
            response = chat_service.chat_with_tools(
                message=message,
                user_id=user_id,
                chat_history=history,
                images=images if images else None
            )
            
            # Clean up temp images
            for img_path in images:
                if os.path.exists(img_path):
                    os.remove(img_path)
            
            # Check guardrails on output
            output_check = GuardrailsService.check_content(
                response['answer'],
                user_id,
                'output'
            )
            
            if not output_check['passed']:
                response['answer'] = output_check['cleaned_content']
            
            return ToolChatResponseSchema().dump(response), 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': f'Chat failed: {str(e)}'}, 500

@chat_ns.route('/history')
class ChatHistory(Resource):
    @chat_ns.doc('get_history')
    @chat_ns.marshal_list_with(chat_history_model)
    @jwt_required()
    def get(self):
        """Get chat history"""
        try:
            user_id = get_jwt_identity()
            chat_service = ChatService()
            history = chat_service.get_chat_history(user_id, limit=50)
            return ChatHistorySchema(many=True).dump(history), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @chat_ns.doc('clear_history')
    @jwt_required()
    def delete(self):
        """Clear chat history"""
        try:
            user_id = get_jwt_identity()
            chat_service = ChatService()
            result = chat_service.clear_chat_history(user_id)
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 500
